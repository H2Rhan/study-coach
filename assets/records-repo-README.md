# study-records

Study records written by the `study-coach` skill. Structure is managed by the skill; keep
edits within the note bodies.

| Folder | Contents |
|---|---|
| `progress/` | Where each course or topic stands: steps done, questions attempted, layers still unverified |
| `mistake-books/` | Wrong answers: question, my answer, correct answer, cause of error, test point, one-line takeaway |
| `summaries/` | Knowledge summaries, review cheat cards, knowledge skeletons |

## Syncing

```bash
python "<skill-dir>/scripts/sync_records.py" --message "update: <course> <what>" --dry-run
```

The script normalizes every tracked file to LF before pushing, because the pusher uploads
raw working-tree bytes and `core.autocrlf=true` would otherwise write CRLF into the remote
blob. Push once per study cycle, not once per question.

## Conventions

- One file per course or topic; split only past roughly 300 lines.
- Record facts only (date, item, result, note) — no transient errors or chatter.
- Mark anything unconfirmed as `未验证` / `unverified` rather than omitting it.
