# study-coach

A **four-mode study companion skill** for AI coding agents (Claude Code / WorkBuddy and anything else that
reads the `SKILL.md` convention). It turns an agent from "answer machine" into a coach: it walks you through
homework step by step, grades your answers item by item, decomposes a topic into foundations, and drills you
before an exam.

Ships with **no personal data** — paths, records location, and optional identity fields all come from a local
config file that `scripts/setup.py` generates.

## The four modes

| Mode | You give it | What it does | You end up with |
|---|---|---|---|
| **1 · Homework guide** | An assignment (PDF / image / DOCX) | Splits it into 3–8 steps, explains only the current step, checks the screenshot you send back, and refuses to spoil later steps | A submittable report (DOCX/PDF), built from the evidence you actually produced |
| **2 · Quiz grading** | A problem set + short messages like `2.3 12 C` | Indexes every question first, grades each answer independently, adds a 2–3 sentence note when you're right and a real error analysis when you're wrong | A mistake notebook, not a wall of text |
| **3 · Knowledge breakdown** | "Explain X" | Builds a dependency tree of the foundational layers, then teaches one layer per turn with a mini-check before advancing | A full-tree cheat sheet + one-page reference table |
| **4 · Review & mock test** | Slides, lecture notes, past papers | Inventories the material (and tells you what's missing), builds a knowledge skeleton, or issues mock tests with the answers kept separate | Summary doc, score breakdown, targeted review plan |

Cross-cutting behaviour: it reads its source material before speaking, never fabricates results (unverified
values become placeholders), always advances one step at a time, and syncs progress to a folder or private
GitHub repo so a later session can pick up where you left off.

## Install

The repository root **is** the skill folder, so cloning is enough:

```bash
git clone https://github.com/<owner>/study-coach.git ~/.workbuddy/skills/study-coach
```

Or unzip a release archive into your skills directory:

```bash
unzip study-coach.zip -d ~/.workbuddy/skills/
```

Or copy a project-scoped install:

```bash
cp -r study-coach <your-project>/.workbuddy/skills/
```

## Configure (one time)

```bash
python ~/.workbuddy/skills/study-coach/scripts/setup.py
```

It writes the config, creates the records folders, prepares the deliverables directory, and optionally creates
the private GitHub repo used for syncing. Non-interactive flags and the full key reference are in
[`references/setup.md`](references/setup.md).

```bash
# minimal, no GitHub
python .../scripts/setup.py --non-interactive \
  --deliverables-dir "$HOME/study/submissions" \
  --records-root "$HOME/study-records"

# with GitHub sync
python .../scripts/setup.py --non-interactive \
  --records-backend github --records-repo "youruser/study-records"
```

Check it at any time:

```bash
python .../scripts/setup.py --show
```

## Then just talk to your agent

> "Here's my lab assignment, walk me through it."
>
> "2.3 12 C"
>
> "Break down virtual memory for me."
>
> "Here are all the lecture slides — help me review, then quiz me."

The skill routes on intent. If it can't tell which mode you mean, it asks once, with four options.

## What's in here

```
SKILL.md                        routing, global rules, deliverable pipeline
references/
  setup.md                      install + configuration reference
  mode1-homework.md             screenshot-guided homework workflow
  mode2-quiz.md                 grading loop + mistake notebook
  mode3-knowledge.md            dependency-tree teaching
  mode4-review.md               summary / mock test / review companion
  record-sync.md                records layout, line-ending handling, sync
scripts/
  setup.py                      first-run configuration
  study_config.py               config loader (stdlib only)
  sync_records.py               discover + normalize + sync records
  github_push.py                self-contained GitHub REST pusher (stdlib only)
assets/
  config.example.json           documented config example
  records-repo-README.md        README seeded into your records folder
  templates/                    progress / mistake book / summary, in Chinese and English
```

All scripts use the Python standard library only. Optional companion skills (polished Word generation, an
HTML→PDF report pipeline) are used when present and gracefully skipped when absent — see
[`references/setup.md`](references/setup.md#6-optional-companion-skills).

## Platform support

| Capability | Windows | macOS / Linux |
|---|---|---|
| Records / config / sync | yes | yes |
| `.docx` output | yes | yes |
| `.pdf` export | Microsoft Word (COM) | LibreOffice (`soffice --headless`) |

If no PDF route exists, the skill delivers the `.docx` and says so rather than failing silently.

## License

MIT — see [LICENSE](LICENSE).
