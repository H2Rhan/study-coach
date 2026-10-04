#!/usr/bin/env python3
"""Sync study records (progress / mistake books / summaries) to their destination.

Two backends, chosen by `records.backend` in the config:
  - "local"  : the files simply live under records.local_root. Nothing else happens.
  - "github" : the files are additionally pushed to records.repo over the GitHub REST API.

Before pushing, every tracked file is normalized from CRLF to LF at byte level.
`github_push` uploads the raw working-tree bytes, so on a machine with
`core.autocrlf=true` CRLF would otherwise land in the remote blob and produce
line-ending-only diffs against every local hash.

Usage:
    python sync_records.py --message "update: chapter 3 progress" --dry-run
    python sync_records.py --message "update: chapter 3 progress"
    python sync_records.py --message "add: review summary" --file summaries/algorithms.md
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import github_push  # noqa: E402
import study_config  # noqa: E402

TRACKED_DIRS = ("progress", "mistake-books", "summaries")
TRACKED_SUFFIXES = (".md", ".markdown", ".txt")


def discover(root: Path) -> list[str]:
    """Return repo-relative paths of everything that should travel with the records."""
    found: list[str] = []
    readme = root / "README.md"
    if readme.is_file():
        found.append("README.md")
    for sub in TRACKED_DIRS:
        base = root / sub
        if not base.is_dir():
            continue
        for dirpath, _dirs, filenames in os.walk(base):
            for name in sorted(filenames):
                if not name.lower().endswith(TRACKED_SUFFIXES):
                    continue
                rel = os.path.relpath(os.path.join(dirpath, name), root)
                found.append(rel.replace(os.sep, "/"))
    return sorted(found)


def normalize_lf(path: Path) -> int:
    """Rewrite CRLF as LF at byte level. Returns how many pairs were replaced."""
    raw = path.read_bytes()
    fixed = raw.replace(b"\r\n", b"\n")
    if fixed != raw:
        path.write_bytes(fixed)
    return raw.count(b"\r\n")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="Sync study-coach records")
    parser.add_argument("--message", help="commit message (required for the github backend)")
    parser.add_argument("--file", dest="files", action="append",
                        help="repo-relative path; repeatable. Defaults to auto-discovery.")
    parser.add_argument("--dry-run", action="store_true",
                        help="show what would change without pushing")
    parser.add_argument("--config", help="path to a config file, overriding resolution")
    args = parser.parse_args()

    if args.config:
        os.environ[study_config.ENV_VAR] = args.config

    cfg, cfg_path = study_config.load()
    records = cfg.get("records") or {}
    backend = records.get("backend", "local")
    root = study_config.records_root(cfg)

    if not root.is_dir():
        print(f"records root does not exist yet: {root}", file=sys.stderr)
        print("run scripts/setup.py to create the folder structure", file=sys.stderr)
        return 1

    files = args.files or discover(root)
    if not files:
        print(f"no record files found under {root}; nothing to sync")
        return 0

    replaced = 0
    for rel in files:
        path = root / rel.replace("/", os.sep)
        if not path.is_file():
            print(f"error: missing file: {rel}", file=sys.stderr)
            return 1
        replaced += normalize_lf(path)
    print(f"normalized {replaced} CRLF occurrence(s) across {len(files)} file(s)")
    print(f"records root : {root}")
    print(f"config       : {cfg_path}")

    if backend != "github":
        print(f"backend is '{backend}'; files are already saved locally, nothing to push")
        return 0

    repo = records.get("repo")
    if not repo:
        print("error: records.repo is empty but records.backend is 'github'", file=sys.stderr)
        return 1
    if not args.message:
        print("error: --message is required for the github backend", file=sys.stderr)
        return 1

    branch = records.get("branch", "main")
    print(f"remote       : {repo} ({branch})")
    return github_push.push(
        repo=repo,
        branch=branch,
        root=str(root),
        files=files,
        message=args.message.strip(),
        author_name=(cfg.get("identity") or {}).get("name") or "study-coach",
        author_email="study-coach@users.noreply.github.com",
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    sys.exit(main())
