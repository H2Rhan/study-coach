# Mode 4 — Review & Mock Test

Three sub-flows. Pick according to what the user asked for; they can be combined (summarize, then test, then
produce a targeted review list).

## Sub-flow A — Automatic Summary From Slides / Notes

1. **Inventory first.** List every file read, its page count, and the chapters covered. Point out gaps
   explicitly ("your set is missing chapter 6") rather than summarizing an incomplete set silently.
2. **Build the knowledge skeleton** in three layers: chapter → knowledge point → exam angle. Mark emphasis
   (high / medium / low) **only when there is evidence** — repeated emphasis in the slides, instructor annotations,
   or past papers. Without evidence, do not invent an exam-frequency rating.
3. **Produce one cheat card per chapter**: core concepts / key formulas or procedures / commonly confused pairs /
   representative question.
4. **Deliver** a `.docx` (plus `.pdf` when it will be printed or submitted), copy it to the user's directory, and
   push the markdown source to `summaries/`.

Prefer visuals over prose: a skeleton graph for the whole course, a comparison table for confusable concepts, a
timeline for anything process-based.

## Sub-flow B — Mock Test

1. **Confirm the parameters in one round**: question types, count, scope (which chapters), difficulty, time limit
   (and whether it is actually timed). Ask all of it once; do not trickle questions.
2. **Issue one batch at a time** — default 5 questions, or the count the user specifies. Match the real exam's
   format (for a computer-science exam: single choice, multiple choice, fill-in, short answer, and for coding
   courses, hand-written code).
3. **Keep answers strictly separate from questions.** Place all answers after the last question, behind a clear
   separator, so the user cannot read them by accident while scrolling. Under no circumstances interleave an
   answer under its question.
4. **Grade after receiving the user's answers**: per-question verdict, points awarded, and the reason for each
   error. Then report total score and the distribution of weak areas — not just the total.
5. **Close the loop**: route weak areas back to sub-flow A for a targeted review list, or generate a mistake
   notebook in the mode 2 format (`references/mode2-quiz.md`) so the two modes share one artifact shape.
6. The mock test itself is usually not a deliverable; do not create files unless the user wants the paper or the
   graded result saved. Score and weak-area summary go into the progress file.

## Sub-flow C — Review Companion (recall practice)

- Run a question → answer → patch loop. The skill asks, the user answers, the skill fills the gap. Keep the
  asking short; this is a drill, not a lecture.
- Apply a spaced-repetition schedule: write a "review today / tomorrow / in three days" checklist into the
  progress file, and on a later session check that list first and re-quiz those items before new material.
- Weight the order toward `未验证` and previously wrong items from the progress and mistake files.

## Rules

- The scope of a review is bounded by the material the user actually provided. If he asks about a chapter that is
  not in the uploads, say so and offer either to work from general knowledge (marked as such) or to wait for the
  file.
- Distinguish clearly between "stated in your slides" and "general knowledge about this topic". The user will be
  examined on the former.
- Do not produce a full mock exam plus its answers plus a review plan in a single turn when he asked for one of
  them. One unit per turn, matching the rhythm of the other modes.
