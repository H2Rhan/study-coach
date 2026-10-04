#!/usr/bin/env python3
"""Self-contained GitHub pusher (stdlib only).

Deliberately standalone so the study-coach skill works on a machine that has no other
skills installed. Reads nothing but the explicit file list it is given, uploads the raw
working-tree bytes, and never prints a credential.

Token resolution order:
  1. $GITHUB_TOKEN or $GH_TOKEN
  2. `gh auth token`
  3. `git credential fill` (system Git Credential Manager)

Usage:
    python github_push.py --repo OWNER/NAME --branch main --root DIR \
        --file progress/x.md --file summaries/y.md --message "update: ..." [--dry-run]

Exit codes: 0 success or nothing to do, 1 error.
"""

from __future__ import annotations

import argparse
import base64
import datetime
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

API = "https://api.github.com"


def _from_env() -> str | None:
    for name in ("GITHUB_TOKEN", "GH_TOKEN"):
        value = os.environ.get(name)
        if value and value.strip():
            return value.strip()
    return None


def _from_gh_cli() -> str | None:
    try:
        proc = subprocess.run(
            ["gh", "auth", "token"], capture_output=True, text=True, timeout=30
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode == 0 and proc.stdout.strip():
        return proc.stdout.strip()
    return None


def _from_credential_manager() -> str | None:
    candidates = ["git"]
    for extra in (
        r"C:\Program Files\Git\cmd\git.exe",
        "/usr/bin/git",
        "/usr/local/bin/git",
    ):
        if os.path.isfile(extra):
            candidates.append(extra)
    for git_bin in candidates:
        try:
            proc = subprocess.run(
                [git_bin, "credential", "fill"],
                input="protocol=https\nhost=github.com\n\n",
                capture_output=True,
                text=True,
                timeout=30,
            )
        except (OSError, subprocess.SubprocessError):
            continue
        if proc.returncode != 0:
            continue
        for line in proc.stdout.splitlines():
            if line.startswith("password="):
                token = line.split("=", 1)[1].strip()
                if token:
                    return token
    return None


def get_token() -> str:
    for getter in (_from_env, _from_gh_cli, _from_credential_manager):
        token = getter()
        if token:
            return token
    raise RuntimeError(
        "no GitHub credential found. Sign in outside this chat "
        "(run `gh auth login`, or `git config --global credential.helper` and push once), "
        "or export GITHUB_TOKEN. Never paste a token into the conversation."
    )


def api(method: str, url: str, token: str, payload=None):
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "study-coach-sync",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:500]
        raise RuntimeError(f"GitHub API {method} {url} failed: HTTP {exc.code}: {detail}") from exc


def remote_bytes(repo: str, branch: str, rel: str, token: str) -> bytes | None:
    """Return the remote file contents, or None when the path does not exist yet."""
    try:
        data = api("GET", f"{API}/repos/{repo}/contents/{rel}?ref={branch}", token)
    except RuntimeError as exc:
        if "HTTP 404" in str(exc):
            return None
        raise
    if data.get("encoding") != "base64":
        raise RuntimeError(f"unexpected encoding for remote file: {rel}")
    return base64.b64decode(data["content"])


def push(repo: str, branch: str, root: str, files: list[str], message: str,
         author_name: str, author_email: str, dry_run: bool = False) -> int:
    token = get_token()
    base = api("GET", f"{API}/repos/{repo}/commits/{branch}", token)
    base_sha = base["sha"]
    base_tree = base["commit"]["tree"]["sha"]

    changed: list[tuple[str, bytes]] = []
    for rel in files:
        abs_path = os.path.join(root, rel.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            raise RuntimeError(f"local file not found: {abs_path}")
        with open(abs_path, "rb") as fh:
            local = fh.read()
        remote = remote_bytes(repo, branch, rel, token)
        same = remote is not None and remote == local
        print(f"{rel}: {'SAME' if same else 'NEW' if remote is None else 'DIFF'}")
        if not same:
            changed.append((rel, local))

    if dry_run:
        print(f"base: {base_sha}")
        print(f"changed: {len(changed)}")
        return 0

    if not changed:
        print("no changed files; nothing to push")
        return 0

    entries = []
    for rel, raw in changed:
        blob = api("POST", f"{API}/repos/{repo}/git/blobs", token, {
            "content": base64.b64encode(raw).decode("ascii"),
            "encoding": "base64",
        })
        entries.append({"path": rel, "mode": "100644", "type": "blob", "sha": blob["sha"]})

    tree = api("POST", f"{API}/repos/{repo}/git/trees", token,
               {"base_tree": base_tree, "tree": entries})

    stamp = datetime.datetime.now(datetime.timezone.utc).astimezone().replace(
        microsecond=0).isoformat()
    identity = {"name": author_name, "email": author_email, "date": stamp}
    commit = api("POST", f"{API}/repos/{repo}/git/commits", token, {
        "message": message,
        "tree": tree["sha"],
        "parents": [base_sha],
        "author": identity,
        "committer": identity,
    })
    api("PATCH", f"{API}/repos/{repo}/git/refs/heads/{branch}", token,
        {"sha": commit["sha"], "force": False})
    print(commit["sha"])
    print(commit["html_url"])
    return 0


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="Push explicit files to GitHub via REST")
    parser.add_argument("--repo", required=True, help="owner/name")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--root", required=True, help="local directory the paths are relative to")
    parser.add_argument("--file", dest="files", action="append", required=True)
    parser.add_argument("--message", required=True)
    parser.add_argument("--author-name", default="study-coach")
    parser.add_argument("--author-email", default="study-coach@users.noreply.github.com")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    try:
        return push(args.repo, args.branch, os.path.abspath(args.root), args.files,
                    args.message.strip(), args.author_name, args.author_email, args.dry_run)
    except Exception as exc:  # noqa: BLE001 - surfaced verbatim to the operator
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
