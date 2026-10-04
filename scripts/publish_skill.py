#!/usr/bin/env python3
"""Publish this skill folder to its own GitHub repository.

Maintainer tool. Pushes the skill directory (the layout expects the repository root to *be*
the skill root, so that `git clone <repo> ~/.workbuddy/skills/study-coach` just works).
`config.json` and `__pycache__` are never uploaded, and every text file is normalized to LF
first because `github_push.py` uploads raw working-tree bytes.

Usage:
    python publish_skill.py --repo OWNER/NAME --dry-run
    python publish_skill.py --repo OWNER/NAME --message "fix: correct grading rule"
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(HERE))

import github_push  # noqa: E402

TEXT_SUFFIXES = {".md", ".py", ".json", ".txt", ".yml", ".yaml", ".toml"}
ALWAYS_INCLUDE = {".gitignore", "LICENSE", "LICENCE"}
SKIP_DIRS = {"__pycache__", ".git", ".venv", "node_modules"}


def collect() -> list[str]:
    files: list[str] = []
    for dirpath, dirnames, filenames in os.walk(SKILL):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            path = Path(dirpath) / name
            if path.suffix.lower() not in TEXT_SUFFIXES and name not in ALWAYS_INCLUDE:
                continue
            rel = path.relative_to(SKILL).as_posix()
            if rel == "config.json":
                continue
            raw = path.read_bytes()
            fixed = raw.replace(b"\r\n", b"\n")
            if fixed != raw:
                path.write_bytes(fixed)
                print(f"normalized CRLF: {rel}")
            files.append(rel)
    return sorted(files)


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="Publish the study-coach skill folder")
    parser.add_argument("--repo", required=True, help="owner/name")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--message", default="chore: update study-coach")
    parser.add_argument("--author-name", default="study-coach")
    parser.add_argument("--author-email", default="study-coach@users.noreply.github.com")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    files = collect()
    print(f"\n{len(files)} file(s) from {SKILL}")
    return github_push.push(
        repo=args.repo,
        branch=args.branch,
        root=str(SKILL),
        files=files,
        message=args.message,
        author_name=args.author_name,
        author_email=args.author_email,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    sys.exit(main())
