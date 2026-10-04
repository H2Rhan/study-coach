# Changelog

All notable changes to this skill. Versions follow [Semantic Versioning](https://semver.org/).

## [2.1.0] — 2026-10-04

### Added
- README artwork: banner, four-mode cards, session loop, behaviour comparison, dependency tree, records flow,
  and a quickstart strip. Rendered from HTML sources kept under `assets/images/_src/`.
- `scripts/publish_skill.py` — maintainer tool that pushes this folder to its own repository.
- GitHub Actions check that compiles the scripts, runs `setup.py` and `sync_records.py` end to end on Linux,
  and fails if an absolute personal path is committed.
- `CHANGELOG.md`.

### Changed
- README restructured: contents list, badges, an explicit "why this exists", a design-principles table, and an FAQ.

### Fixed
- `publish_skill.py` only uploaded text files, so images were silently skipped. Binary assets
  (`.png`, `.jpg`, `.webp`, `.gif`, `.svg`, `.pdf`) and `.html` sources are now included.

## [2.0.0] — 2026-10-04

### Added
- Configuration system: `scripts/study_config.py` (loader) and `scripts/setup.py` (first-run setup, interactive
  or flag-driven). The skill itself now contains **no personal data** — no paths, no identity, no repo name.
- `scripts/github_push.py` — a self-contained, stdlib-only GitHub REST pusher, so the skill no longer depends on
  any other skill being installed. Token resolution: `$GITHUB_TOKEN` / `$GH_TOKEN` → `gh auth token` →
  `git credential fill`.
- `references/setup.md` — install, configuration reference, platform notes, troubleshooting.
- English variants of all three record templates (`*-template.en.md`).
- `LICENSE` (MIT) and `.gitignore`.

### Changed
- Records syncing is now backend-selectable via `records.backend`: `local` (default) or `github`.
- The deliverable pipeline is documented with explicit fallbacks, so a missing companion skill degrades instead
  of failing silently.
- Records folders and templates are described by config keys rather than literal paths.

### Fixed
- `setup.py --config PATH` only redirected the *write*; the read still went to the default location, so a freshly
  created config inherited the identity fields of an existing one. The environment variable is now set before
  loading, redirecting both.

## [1.0.0] — 2026-10-04

### Added
- Initial release: one skill with four modes — screenshot-guided homework help, quiz grading with a mistake
  notebook, dependency-tree knowledge breakdown, and exam review with mock tests.
