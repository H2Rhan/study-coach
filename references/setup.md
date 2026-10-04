# Install & First-Run Setup

The skill ships with **no personal data** — no paths, no repo names, no student identity. Everything
machine-specific is generated locally by `scripts/setup.py`.

## 1. Install the skill

The skill is just a folder. Put it where the agent looks for skills:

| Host | Location |
|---|---|
| WorkBuddy | `~/.workbuddy/skills/study-coach/` (user scope, all projects) or `<project>/.workbuddy/skills/study-coach/` |
| Any agent reading `SKILL.md` conventions | anywhere on disk; point the agent at `SKILL.md` |

Three ways to get the folder:

```bash
# a) from the release zip
unzip study-coach.zip -d ~/.workbuddy/skills/

# b) git clone
git clone https://github.com/<owner>/study-coach.git ~/.workbuddy/skills/study-coach

# c) copy manually
cp -r /path/to/study-coach ~/.workbuddy/skills/
```

Then confirm the layout:

```bash
ls ~/.workbuddy/skills/study-coach/
# SKILL.md  references/  scripts/  assets/
```

No restart is needed for a user-level skill to become available.

## 2. Configure it

Run the setup script once. It writes the config, creates the records folders, and prepares the
deliverables directory.

**Interactive** (in a terminal):

```bash
python ~/.workbuddy/skills/study-coach/scripts/setup.py
```

**Non-interactive** (typical when an agent runs it on your behalf):

```bash
python ~/.workbuddy/skills/study-coach/scripts/setup.py --non-interactive \
  --output-language auto \
  --deliverables-dir "$HOME/study/submissions" \
  --records-backend local \
  --records-root "$HOME/study-records"
```

**With GitHub sync for the records:**

```bash
python ~/.workbuddy/skills/study-coach/scripts/setup.py --non-interactive \
  --records-backend github \
  --records-repo "youruser/study-records" \
  --records-root "$HOME/study-records" \
  --identity-student-id 2025001 --identity-name "Zhang San"
```

`--records-visibility` defaults to `private`. The script creates the repo with `gh` if it is
available and the repo does not exist; pass `--no-repo-create` to skip that.

Verify at any time:

```bash
python ~/.workbuddy/skills/study-coach/scripts/setup.py --show
```

## 3. Configuration reference

Config file resolution order (first hit wins):

1. `$STUDY_COACH_CONFIG`
2. `~/.workbuddy/study-coach.config.json`  ← default
3. `<skill-dir>/config.json`

A documented example is at `assets/config.example.json`.

| Key | Default | Meaning |
|---|---|---|
| `output_language` | `auto` | `auto` follows the language you write in. `en` / `zh` force one. |
| `records.backend` | `local` | `local` keeps records on disk only. `github` also pushes them. |
| `records.local_root` | `~/study-records` | Where `progress/`, `mistake-books/`, `summaries/` live. |
| `records.repo` | *(empty)* | `owner/name`, required when the backend is `github`. |
| `records.branch` | `main` | Target branch. |
| `records.remote_visibility` | `private` | Advisory; used only when setup creates the repo. |
| `deliverables.dir` | `auto` | `auto` = Desktop if it exists, else home. Finished documents are copied here. |
| `deliverables.formats` | `["docx"]` | Default output format. |
| `deliverables.submission_formats` | `["docx","pdf"]` | Formats produced when the work is handed in. |
| `identity.student_id` | *(empty)* | Optional; used in submission filenames. |
| `identity.name` | *(empty)* | Optional; used in submission filenames. |
| `identity.filename_pattern` | `{student_id}_{name}_{assignment}.{ext}` | Empty identity fields collapse automatically, so `_作业3` becomes `作业3`. |
| `tone.colloquial` / `tone.no_padding` | `true` | Keep replies direct and free of filler. |

## 4. GitHub credentials (only for the `github` records backend)

The pusher resolves a token in this order and never prints it:

1. `$GITHUB_TOKEN` or `$GH_TOKEN`
2. `gh auth token`
3. `git credential fill` (system credential manager)

So either export a token, or sign in once with `gh auth login` / a normal `git push`. Never paste a
token into a conversation.

## 5. Platform notes

| Capability | Windows | macOS / Linux |
|---|---|---|
| Records sync | full | full |
| `.docx` output | via the `tencent-docx` / `html-to-docx` skills when present | same, or `python-docx` directly |
| `.pdf` export | Word COM (requires Microsoft Word) | `soffice --headless --convert-to pdf` (LibreOffice) or `pandoc` |
| PDF text/dimension checks | `pymupdf` | `pymupdf` |

The skill degrades gracefully: if a companion skill is missing it falls back to a plain library
call, and if no PDF path exists it delivers the `.docx` and says so rather than failing silently.

## 6. Optional companion skills

These are **not required**. When present, the skill uses them; when absent, it falls back.

| Companion skill | What it adds | Fallback |
|---|---|---|
| `tencent-docx` | Polished Word generation | `python-docx` |
| `html-report-to-pdf-submit` | HTML → DOCX → PDF with a pre-delivery self-check | `python-docx` + LibreOffice/Word |
| `github-api-direct-push` | A richer push script with per-file verification | the bundled `scripts/github_push.py` |

## 7. Verification checklist

```bash
python ~/.workbuddy/skills/study-coach/scripts/setup.py --show
python ~/.workbuddy/skills/study-coach/scripts/sync_records.py --message "test" --dry-run
```

For the `local` backend the second command should report the records root and say there is nothing
to push. For the `github` backend it should print `SAME` / `DIFF` / `NEW` per file and, without
`--dry-run`, a commit SHA and URL.

## 8. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `records root does not exist yet` | Run `setup.py` — it creates `progress/`, `mistake-books/`, `summaries/`. |
| `no GitHub credential found` | Sign in outside the chat: `gh auth login`, or export `GITHUB_TOKEN`. |
| Every file reports `DIFF` although nothing changed | Line endings. `sync_records.py` normalizes CRLF→LF automatically; run it rather than pushing by hand. |
| GitHub returns 403/404 | Wrong repo name, or the token lacks `repo` scope. The skill stops rather than retrying. |
| PDF export fails | No Word (Windows) or LibreOffice (macOS/Linux). Deliver the `.docx` and tell the user. |
