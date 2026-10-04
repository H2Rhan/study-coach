#!/usr/bin/env python3
"""Configuration loader for the study-coach skill.

Resolution order (first existing wins):
  1. $STUDY_COACH_CONFIG
  2. ~/.workbuddy/study-coach.config.json
  3. <skill-dir>/config.json

Nothing personal is baked into the skill. Every path, repo name, and identity field
comes from this config file, which each user generates with scripts/setup.py.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

ENV_VAR = "STUDY_COACH_CONFIG"
DEFAULT_FILENAME = "study-coach.config.json"
SKILL_DIR = Path(__file__).resolve().parent.parent


def _home() -> Path:
    return Path(os.path.expanduser("~"))


def _default_deliverables_dir() -> str:
    """Prefer the Desktop when it exists, otherwise the home directory."""
    desktop = _home() / "Desktop"
    return str(desktop if desktop.is_dir() else _home())


DEFAULTS: dict[str, Any] = {
    # "auto" follows whatever language the user writes in.
    "output_language": "auto",

    "records": {
        # "local" writes the files under records.local_root and stops there.
        # "github" additionally pushes them to records.repo through the REST API.
        "backend": "local",
        "local_root": str(_home() / "study-records"),
        "repo": "",
        "branch": "main",
        # Advisory only; setup.py reads it when it creates the repo.
        "remote_visibility": "private",
    },

    "deliverables": {
        # "auto" resolves to the Desktop when it exists, else the home directory.
        "dir": "auto",
        "formats": ["docx"],
        "submission_formats": ["docx", "pdf"],
    },

    "identity": {
        # Leave empty if you would rather name files yourself. Both are optional.
        "student_id": "",
        "name": "",
        "filename_pattern": "{student_id}_{name}_{assignment}.{ext}",
    },

    "tone": {
        "colloquial": True,
        "no_padding": True,
    },
}


def config_path() -> Path:
    """Return the path that load() would read, whether or not it exists."""
    env = os.environ.get(ENV_VAR)
    if env:
        return Path(env)
    user_level = _home() / ".workbuddy" / DEFAULT_FILENAME
    if user_level.exists():
        return user_level
    local = SKILL_DIR / "config.json"
    if local.exists():
        return local
    return user_level


def _merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out


def load() -> tuple[dict[str, Any], Path]:
    """Return (effective_config, path_read_from). Missing file yields defaults."""
    path = config_path()
    if path.is_file():
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"config is not valid JSON: {path}: {exc}") from exc
        return _merge(DEFAULTS, raw), path
    return json.loads(json.dumps(DEFAULTS)), path


def save(cfg: dict[str, Any], path: Path | None = None) -> Path:
    target = path or config_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return target


def missing_required(cfg: dict[str, Any]) -> list[str]:
    """Return human-readable descriptions of what still needs configuring."""
    problems: list[str] = []
    records = cfg.get("records", {})
    if not records.get("local_root"):
        problems.append("records.local_root")
    if records.get("backend") == "github" and not records.get("repo"):
        problems.append("records.repo (required when records.backend is 'github')")
    return problems


def deliverables_dir(cfg: dict[str, Any]) -> Path:
    configured = (cfg.get("deliverables") or {}).get("dir") or "auto"
    if configured == "auto":
        return Path(_default_deliverables_dir())
    return Path(os.path.expanduser(configured))


def records_root(cfg: dict[str, Any]) -> Path:
    raw = (cfg.get("records") or {}).get("local_root") or str(_home() / "study-records")
    return Path(os.path.expanduser(raw))


def format_deliverable_name(cfg: dict[str, Any], assignment: str, ext: str) -> str:
    identity = cfg.get("identity") or {}
    pattern = identity.get("filename_pattern") or "{assignment}.{ext}"
    values = {
        "student_id": identity.get("student_id") or "",
        "name": identity.get("name") or "",
        "assignment": assignment,
        "ext": ext,
    }
    name = pattern.format(**values)
    # Collapse separators left behind by empty identity fields: "_作业3" -> "作业3".
    while "__" in name:
        name = name.replace("__", "_")
    return name.strip("_")


if __name__ == "__main__":
    cfg, path = load()
    print(f"config path : {path}  ({'found' if path.is_file() else 'NOT FOUND, using defaults'})")
    print(f"records     : backend={cfg['records']['backend']} root={records_root(cfg)}")
    print(f"deliverables: {deliverables_dir(cfg)}")
    problems = missing_required(cfg)
    print(f"problems    : {problems if problems else 'none'}")
