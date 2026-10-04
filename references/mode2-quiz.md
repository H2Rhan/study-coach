# Mode 2 — Quiz Grading & Mistake Notebook

The user reads a document of questions and reports answers as short messages like `2.3 12 C` (section, question
number, answer). The job is to grade independently, add a brief note when correct, give a real error analysis
when wrong, and accumulate a mistake notebook.

## Phase 0 — Build the question index first

Parse the **entire** document and post an index table: question number, one-line summary of what it asks, page
number. This is not for teaching — it is so that a later `2.3 12` resolves instantly, and so total progress can
be computed.

- Scanned PDFs with no text layer → OCR first (Tesseract with the language pack matching the document). A
  one-question-per-page book can be located by page number.
- Record the numbering style actually used in the document (e.g. `2.3 12`) and mirror it back to the user.
- Note the chapter boundaries and how many questions each chapter has — this becomes the progress denominator.
- If the document spans hundreds of pages, index the current chapter fully and note how far the index reaches.
  Do not silently index only the first few pages.

## Phase 1 — The per-question loop

When the user reports a question number and answer:

**a. Locate the original question.** Read that page / paragraph (OCR if needed). If it cannot be located, ask one
short question — never guess what the question says.

**b. Grade independently.** Do not assume the user is right, and do not assume he is wrong. For contested items,
items with version differences, or items whose correct answer depends on a convention, search the web to verify
and state the basis. If the printed answer key and the correct answer disagree, say so explicitly.

**c. Respond with the amount of information the case deserves:**

- **Correct answer → 2–3 sentences total.** One sentence on why it is right, one or two on a commonly confused
  neighbour or a useful extension. No full derivation, no restated question, no table. A past attempt turned
  every multiple-choice question into a mini-essay and was rejected.
- **Wrong answer →** the specific cause of the error ("you mixed up X with Y", "the loop bound is off by one")
  → the correct option plus the reason → the underlying test point in one sentence. A small comparison table is
  appropriate only when the confusion is genuinely tabular.
- **Ambiguous / contested question →** state the ambiguity, give the two readings, and cite the basis. Do not
  force a verdict.

**d. Append to the mistake notebook** only when the answer was wrong, or when the user says "note this one down"
for a valuable correct answer. Never insert correct answers by default.

**e. Update the progress file**: question numbers attempted, right/wrong, running accuracy, date.

## Phase 2 — The mistake notebook

Use `assets/templates/mistake-book-template.md`. One file per course, sections per chapter. Each entry:

- Question number + page
- Question summary (one line, not the full text)
- My answer / correct answer
- Cause of error
- Test point
- One-line takeaway to remember

Keep correct answers out unless the user asks. The notebook's value is that it is short enough to re-read the
night before an exam.

Deliverable: when the user says "organize the mistake notebook" or a chapter is finished, produce a `.docx`
(plus `.pdf` when it will be handed in), copy it into `deliverables.dir` from the config under a per-course
subfolder, and push the markdown source to `mistake-books/` in the records folder.

## Adapting To Short-Message Habits

Many users send **one question per message**. Do not prompt them to batch, and do not queue up extra questions.

- Because the input is short, the reply must be short too. A three-line answer is the target for a correct one.
- If several questions arrive at once, that is not an invitation to expand several long analyses — apply the
  same length discipline to each.
- The message is a report, not a request. Do not open with pleasantries; lead with the verdict.
- If the answer is correct but arrived at by wrong reasoning, say so — that is the one case where a correct
  answer still deserves a longer reply.
- If `tone.colloquial` is set, drop the hedging and the throat-clearing entirely.

## Pitfalls

- Do not rely on the answer key printed in a companion volume; it is frequently absent or wrong. Grade from first
  principles, verify with search when unsure.
- Do not re-read the whole document for each question; the index built in phase 0 exists to make lookups cheap.
- Do not lose track of which questions were already done. Progress lives in `progress/<course>.md`, so a new
  session can resume without asking.
