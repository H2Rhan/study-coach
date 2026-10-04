#!/usr/bin/env python3
"""First-run setup for the study-coach skill.

Writes the config file, creates the records folder structure, and (optionally) creates
the private GitHub repo used to sync records. Run it once per machine.

Interactive:
    python setup.py

Non-interactive (the usual case when an agent runs it on the user's behalf):
    python setup.py --non-interactive \
        --deliverables-dir "D:/study/submissions" \
        --records-backend github \
        --records-repo "myuser/study-records" \
        --identity-student-id 2025001 --identity-name "Zhang San"

Inspect the effective configuration at any time:
    python setup.py --show
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import study_config  # noqa: E402

SKILL_DIR = Path(__file__).resolve().parent.parent
RECORDS_README = SKILL_DIR / "assets" / "records-repo-README.md"


def _ask(prompt: str, default: str) -> str:
    try:
        answer = input(f"{prompt} [{default}]: ").strip()
    except EOFError:
        return default
    return answer or default


def _scaffold_records(root: Path) -> list[str]:
    created: list[str] = []
    for sub in ("progress", "mistake-books", "summaries"):
        target = root / sub
        if not target.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            created.append(str(target))
    readme = root / "README.md"
    if not readme.exists() and RECORDS_README.is_file():
        shutil.copyfile(RECORDS_README, readme)
        created.append(str(readme))
    return created


def _maybe_create_repo(repo: str, visibility: str) -> str | None:
    """Create the GitHub repo when gh is available and the repo does not exist."""
    if shutil.which("gh") is None:
        return "gh CLI not found — create the repo manually, then re-run setup"
    probe = subprocess.run(["gh", "repo", "view", repo], capture_output=True, text=True)
    if probe.returncode == 0:
        return None
    flag = "--private" if visibility == "private" else "--public"
    made = subprocess.run(
        ["gh", "repo", "create", repo, flag, "--add-readme"],
        capture_output=True, text=True,
    )
    if made.returncode != 0:
        return f"could not create {repo}: {made.stderr.strip()[:300]}"
    return f"created https://github.com/{repo}"


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="Configure the study-coach skill")
    parser.add_argument("--show", action="store_true", help="print config and exit")
    parser.add_argument("--non-interactive", action="store_true",
                        help="never prompt; use flags and defaults")
    parser.add_argument("--config", help="write the config here instead of the default path")
    parser.add_argument("--output-language", choices=["auto", "en", "zh"])
    parser.add_argument("--deliverables-dir")
    parser.add_argument("--records-backend", choices=["local", "github"])
    parser.add_argument("--records-root")
    parser.add_argument("--records-repo")
    parser.add_argument("--records-branch")
    parser.add_argument("--records-visibility", choices=["private", "public"],
                        default="private")
    parser.add_argument("--identity-student-id")
    parser.add_argument("--identity-name")
    parser.add_argument("--no-repo-create", action="store_true",
                        help="skip creating the GitHub repo even for the github backend")
    args = parser.parse_args()

    # --config must redirect both the read and the write. Setting it before load()
    # stops an existing config elsewhere from leaking values (e.g. someone else's
    # identity) into a freshly created one.
    if args.config:
        os.environ[study_config.ENV_VAR] = args.config

    cfg, path = study_config.load()

    if args.show:
        print(f"config path : {path}  ({'found' if path.is_file() else 'NOT FOUND, defaults in use'})")
        print(f"records     : backend={cfg['records']['backend']} root={study_config.records_root(cfg)}")
        print(f"              repo={cfg['records']['repo'] or '(none)'} branch={cfg['records']['branch']}")
        print(f"deliverables: {study_config.deliverables_dir(cfg)} formats={cfg['deliverables']['formats']}")
        print(f"identity    : id={cfg['identity']['student_id'] or '(empty)'} name={cfg['identity']['name'] or '(empty)'}")
        print(f"language    : {cfg['output_language']}")
        problems = study_config.missing_required(cfg)
        print(f"problems    : {problems if problems else 'none'}")
        return 0

    interactive = not args.non_interactive and sys.stdin.isatty()

    if interactive:
        print("study-coach setup. Press Enter to accept each default.\n")

    # --- language -----------------------------------------------------------
    if args.output_language:
        cfg["output_language"] = args.output_language
    elif interactive:
        cfg["output_language"] = _ask(
            "Output language (auto / en / zh)", cfg["output_language"])

    # --- deliverables -------------------------------------------------------
    default_dir = str(study_config.deliverables_dir(cfg))
    if args.deliverables_dir:
        cfg["deliverables"]["dir"] = args.deliverables_dir
    elif interactive:
        cfg["deliverables"]["dir"] = _ask("Where should finished documents be copied?", default_dir)

    # --- records ------------------------------------------------------------
    if args.records_backend:
        cfg["records"]["backend"] = args.records_backend
    elif interactive:
        cfg["records"]["backend"] = _ask(
            "Records backend (local / github)", cfg["records"]["backend"])

    if args.records_root:
        cfg["records"]["local_root"] = args.records_root
    elif interactive:
        cfg["records"]["local_root"] = _ask(
            "Local records folder", str(study_config.records_root(cfg)))

    if args.records_repo:
        cfg["records"]["repo"] = args.records_repo
    elif interactive and cfg["records"]["backend"] == "github":
        cfg["records"]["repo"] = _ask(
            "GitHub repo for records (owner/name)", cfg["records"]["repo"])

    if args.records_branch:
        cfg["records"]["branch"] = args.records_branch
    if args.records_visibility:
        cfg["records"]["remote_visibility"] = args.records_visibility

    # --- identity (optional) ------------------------------------------------
    if args.identity_student_id is not None:
        cfg["identity"]["student_id"] = args.identity_student_id
    elif interactive:
        cfg["identity"]["student_id"] = _ask(
            "Student ID for submission filenames (optional)", cfg["identity"]["student_id"])

    if args.identity_name is not None:
        cfg["identity"]["name"] = args.identity_name
    elif interactive:
        cfg["identity"]["name"] = _ask(
            "Name for submission filenames (optional)", cfg["identity"]["name"])

    # --- write --------------------------------------------------------------
    target = Path(args.config) if args.config else None
    written = study_config.save(cfg, target)

    root = study_config.records_root(cfg)
    created = _scaffold_records(root)
    dest = study_config.deliverables_dir(cfg)
    dest.mkdir(parents=True, exist_ok=True)

    print(f"\nconfig written : {written}")
    print(f"records root   : {root}")
    print(f"deliverables   : {dest}")
    if created:
        print("created        :")
        for item in created:
            print(f"  - {item}")

    if cfg["records"]["backend"] == "github" and not args.no_repo_create:
        repo = cfg["records"]["repo"]
        if repo:
            note = _maybe_create_repo(repo, cfg["records"]["remote_visibility"])
            if note:
                print(f"repo           : {note}")

    problems = study_config.missing_required(cfg)
    if problems:
        print(f"\nstill missing  : {problems}")
        return 1

    print("\nsetup complete. Verify with: python setup.py --show")
    return 0


if __name__ == "__main__":
    sys.exit(main())
