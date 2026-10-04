---
name: study-coach
description: |
  Full-cycle study companion skill with four modes. Mode 1 (homework guide): after the user uploads an
  assignment, break it into steps and lead them one step at a time; the user returns a screenshot per step and
  the skill finally produces a submittable report. Mode 2 (quiz grading): read an entire problem set to build a
  question index, then the user reports "question number + answer" and the skill grades each item independently,
  adding a brief note when correct and a full error analysis when wrong, ending with a mistake notebook.
  Mode 3 (knowledge breakdown): decompose a topic into a dependency tree of foundational layers and teach it
  layer by layer with a check at each layer. Mode 4 (review & mock exam): auto-summarize uploaded PPTs/lecture
  notes into a knowledge skeleton, or generate mock tests and turn the results into a review plan.
  This skill should be used when the user uploads homework / 作业 / 题册 / 卷子 / 课件 / PPT / 讲义 / 复习资料,
  or asks to be walked through an assignment, to have answers graded, to build a mistake notebook, to have a
  topic broken down and explained, to review for an exam, or to sit a mock test. Requires a one-time
  configuration step (scripts/setup.py); see references/setup.md.
agent_created: true
category: capability
version: "2.1.0"
tags: [homework-guide, mistake-notebook, knowledge-breakdown, exam-review, mock-test, screenshot-guided, study-companion, configurable]
---

# Study Coach — Full-Cycle Study Companion

One skill, four modes. Core stance: **be a coach and a sparring partner, not a ghostwriter.** The user wants to
learn or to be tested; a bare answer pasted at them is rarely what is wanted.

The skill contains **no personal data**. Paths, the records location, and optional identity fields are read
from a local config file at runtime.

## Step 0 — Check Configuration

Before the first task on a machine, confirm the config exists:

```bash
python "<skill-dir>/scripts/setup.py" --show
```

- Reports `problems: none` → proceed.
- Reports missing values, or the config file is absent → run `scripts/setup.py` (interactive, or with the
  relevant flags) and tell the user what was configured. Full instructions: `references/setup.md`.
- Never invent a records path or a repo name. Ask, or read the config.

Relevant config keys: `records.*`, `deliverables.dir`, `deliverables.formats`, `identity.*`,
`output_language`, `tone.*`. Everything below refers to these keys rather than to literal paths.

## Step 1 — Route To A Mode

| User signal | Mode | Load |
|---|---|---|
| Uploads an assignment + wants step-by-step guidance | 1 Homework Guide | `references/mode1-homework.md` |
| Uploads a problem set + reports "number, answer" / asks for grading | 2 Quiz Grading | `references/mode2-quiz.md` |
| "Break down X" / "understand X", no assignment, no questions | 3 Knowledge Breakdown | `references/mode3-knowledge.md` |
| Uploads slides/notes + review / summary / mock exam | 4 Review & Mock Test | `references/mode4-review.md` |

If ambiguous, **ask exactly one question** offering the four modes as options. Never run a chain of clarifying
questions. For mixed requests, follow the primary task and add the secondary artifact at the end (e.g. homework
finished → append a list of the mistakes made along the way).

## Global Rules (all four modes)

1. **Read the source material before speaking.** When the user provides a PDF/PPT/image, parse it first (OCR
   scanned pages). Never guess a question's content from its number. If a page cannot be read, say so.
2. **Advance one step at a time.** Unless the user explicitly says "stop guiding me, just give me all the
   answers", never reveal the method or answer for later steps in advance.
3. **Grade independently.** Never assume the user's answer is right or wrong. For contested, obscure, or
   memory-dependent items, verify with WebSearch and cite the basis. Never paper over uncertainty with
   "should be correct".
4. **Never fabricate.** Unknown numbers, run outputs, exam-frequency claims, and conclusions get a
   `【待确认：xxx】` / `[UNCONFIRMED: xxx]` placeholder instead of a plausible-looking invention. Mark what is
   missing and ask the user to fill it.
5. **Do not create files unprompted.** Keep the working process in the conversation. Write to disk only when
   (a) the user explicitly asks for a deliverable, or (b) a full cycle completes (one assignment done / one
   chapter drilled / one course reviewed).
6. **Ship finished files, not drafts.** Default to the formats in `deliverables.formats` (normally `.docx`);
   add the formats in `deliverables.submission_formats` when the work is meant to be handed in. Never hand the
   user a bare `.md` as the deliverable — the `.md` is the source that goes into the records folder.
7. **Copy deliverables to `deliverables.dir`** immediately after generating them, into a per-course
   subfolder. Never leave the only copy in a session working directory; that storage is not durable.
8. **Tone.** Follow `tone.colloquial` / `tone.no_padding`: colloquial, short, direct. No "great question", no
   "hope this helps", no generic padding (platform introductions, design-methodology essays, textbook-style
   experiment objectives, summary tables that merely restate the task). Users who set these flags are highly
   sensitive to filler.

Write user-facing output in `output_language`. With `auto`, match the language the user writes in. The skill's
own documentation is in English; that does not dictate the language of the reply.

## Records

- Location and backend come from `records.*`. Layout: `progress/`, `mistake-books/`, `summaries/`.
- **At session start**, if a matching file exists under `progress/`, read it and use it to answer "where did we
  leave off" — never make the user restate progress.
- Write rules, line-ending handling, and sync commands: `references/record-sync.md`
- One-shot sync: `scripts/sync_records.py` (self-contained; no other skill required)
- Templates: `assets/templates/` — Chinese and English variants of progress, mistake book, and summary.

## Deliverable Pipeline

Prefer a companion skill when it exists; otherwise fall back. Never fail silently.

| Artifact | Preferred | Fallback |
|---|---|---|
| Report with images/tables/code/logs | `html-report-to-pdf-submit` (HTML → DOCX → PDF) | `python-docx` directly |
| Text-only document (mistake book, summary) | `tencent-docx` | `python-docx` |
| Editing a file the user already owns | `tencent-docs-routing` | `python-docx` / direct XML edit |
| PDF export | Word COM on Windows, `soffice --headless` elsewhere | deliver the `.docx` and say PDF is unavailable |

After generation, **self-verify** before delivering: page count, fonts present (no missing-glyph boxes), no
near-empty pages, no dropped images. Then present the files with absolute paths.

## Visualization

In modes 3 and 4, actively prefer inline visuals (dependency trees, knowledge skeleton graphs, comparison
tables, timelines, data-flow diagrams) over pages of prose — they make learning materially more effective.
Do **not** flood mode 1 with visuals; it steals time from the user's own hands-on work.

## Four Modes At A Glance

| | 1 Homework Guide | 2 Quiz Grading | 3 Knowledge Breakdown | 4 Review & Mock Test |
|---|---|---|---|---|
| Opening | Parse requirements → split into 3–8 steps | Parse the whole set → build a question index | Build a foundational dependency tree | Inventory the material → build a knowledge skeleton |
| Rhythm | One step → one screenshot → one confirmation | One question at a time | One layer → explanation → check | One unit → quiz → patch gaps |
| Output per turn | Only the current step | Correct: 2–3 sentences. Wrong: cause + correct answer + key point | One layer's concept + example + mini-check | One batch of questions + answers kept separate |
| Hard rule | Never spoil later steps | Never write an essay for a correct answer | Never advance if the check fails | Answers must not sit next to the questions |
| End artifact | Submittable report | Mistake notebook | Full-tree cheat sheet + one-page table | Summary doc / score + review plan |

## Distribution Notes

The skill is self-contained and portable. Keep it that way: **never write a user's absolute paths, real name,
student ID, or repo name into `SKILL.md` or the files under `references/`, `scripts/`, `assets/`.** All
machine-specific values belong in the config file, which is generated locally and never shipped.

`assets/images/` holds the publishable README artwork and is not part of the skill's runtime behaviour — do not
load it while answering a user. `assets/images/_src/` holds the HTML sources it is rendered from; regenerate
with headless Chrome (`--force-device-scale-factor=2 --window-size=W,H --screenshot=…`) and ship PNG only.
