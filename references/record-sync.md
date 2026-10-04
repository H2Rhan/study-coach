# Records & Sync

Progress, mistake notebooks, and summaries survive across sessions and machines by living in a fixed
folder — optionally a private GitHub repository. The skill reads them at session start and appends at
the end of a cycle.

**Nothing here is hardcoded.** Every path and repo name comes from the config file; see
`references/setup.md` for the resolution order and the full key list. Read the config before doing
anything with records:

```bash
python "<skill-dir>/scripts/setup.py" --show
```

If it reports `problems`, run `scripts/setup.py` first and do not proceed.

## Layout

Relative to `records.local_root`:

| Path | Contents |
|---|---|
| `progress/<course-or-topic>.md` | Steps done, questions attempted, layers unverified, spaced-repetition checklist |
| `mistake-books/<course>.md` | Wrong answers with cause and test point |
| `summaries/<course-or-topic>.md` | Knowledge summaries and cheat cards |
| `README.md` | Folder overview (seeded by setup) |

Templates live at `assets/templates/`. Copy the matching template when creating a file; afterwards
edit in place. Templates ship in both Chinese (`*-template.md`) and English (`*-template.en.md`);
pick according to `output_language` (with `auto`, match the language the user is writing in).

## Session Start

1. Resolve `records.local_root` from the config.
2. Check for a file under `progress/` matching the current course or topic. If one exists, read it
   before responding and use it to state where the previous session stopped.
3. Never ask the user to restate progress the file already records, and never redo completed work.
4. If the folder does not exist, setup has not been run — see `references/setup.md`.

## Writing Rules

- **Incremental edits only.** Edit the relevant rows; never rewrite a whole file, and never
  overwrite sections the user wrote by hand.
- One file per course or topic. Split past roughly 300 lines.
- Record facts, not commentary: date, item (step / question number / layer), result, note. Do not log
  transient failures, tool errors, or chatter.
- Mark uncertainty as `未验证` / `unverified` rather than omitting it.

## Syncing

Use the bundled script — it handles discovery, line-ending normalization, and the chosen backend:

```bash
python "<skill-dir>/scripts/sync_records.py" --message "update: <course> <what>"
```

Add `--dry-run` first to see per-file status (`SAME` / `DIFF` / `NEW`) without committing.

| Backend | Behaviour |
|---|---|
| `local` (default) | The files already live under `records.local_root`; the script reports and exits. |
| `github` | Additionally pushes to `records.repo` on `records.branch` over the REST API. |

**When to sync:** at the end of a cycle (assignment finished, chapter drilled, course reviewed) or
when the user asks. Do **not** sync after every question — that produces dozens of trivial commits.

## Why Line Endings Matter

The pusher uploads the **raw bytes of the working tree**. Where `core.autocrlf=true`, the working
tree holds CRLF while the git object holds LF, so pushing directly writes CRLF into the remote blob
and every local hash then disagrees with the remote. `sync_records.py` rewrites CRLF as LF at byte
level before pushing — never bypass it with `sed`/`grep`, because MSYS grep treats CRLF as a line
terminator and reports misleading counts.

## Credentials

Resolved by `scripts/github_push.py`, in order: `$GITHUB_TOKEN` / `$GH_TOKEN` → `gh auth token` →
`git credential fill`. The token is never printed, logged, or written to disk.

- Lookup fails → ask the user to sign in outside the chat. Never request a token in the conversation.
- GitHub returns 403/404 → stop and report the status. Do not retry in a loop.
- The remote moved ahead → just re-run; the script reads the current branch head as its base.

## Privacy

Records are personal study data. With the `github` backend, keep the repository **private** unless the
user explicitly asks otherwise, and never move a `local`-backend user's files into a remote repo
without being asked.
