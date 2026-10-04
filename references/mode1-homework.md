# Mode 1 — Homework Guide (screenshot-guided)

**Positioning: the skill is the guide, not the ghostwriter.** The user wants to do the work himself and end up
with a submittable report. Handing him the finished answer defeats the purpose and he will push back.

## Phase 0 — Build the assignment card

Parse the assignment (PDF / image / DOCX) **in full before planning anything**. Never plan from page 1 alone.
Extract and post as a short card in the conversation (do not write a file yet):

- Course, assignment number, due date
- Submission requirements: file naming rule, format, whether a PDF is required
- The full task list (every question / every required module)
- Grading points visible in the prompt (what the instructor says gets scored)
- Tools implied by the task (e.g. Vivado, a specific simulator, a language/version)

If anything required is missing (student ID, exact filename pattern, device part number), use a
`【待确认：xxx】` placeholder and ask once — do not silently assume.

## Phase 1 — Split into steps and show only the map

1. Decompose into **3–8 steps**. A step is one action the user can complete in one sitting and prove with a
   single screenshot.
2. Post **only the step titles** so he sees the whole route. Titles are not spoilers; methods are.
3. Then explain step 1 in detail and stop.

Rules:
- Order steps so each one produces visible evidence (a waveform, a log line, a pin assignment, a running
  program) — the report will need that evidence later.
- If a step depends on a tool being installed or a project being created correctly, that setup is its own step.
  Do not fold "create the project" into "implement the circuit".

## Phase 2 — The per-step loop

For each step, repeat exactly this:

**a. Explain the step** with the three-part pattern the user needs (his pain point is not knowing where to
click, not lacking understanding):

> **Where to click** → **what you should see** → **if it does not look like that, check X**

**b. State the evidence.** Tell him precisely what to screenshot: which panel, which time window, what must be
visible in the frame. "Send me a screenshot" without a specification produces unusable screenshots.

**c. Wait for the screenshot, then actually look at it.** Check it point by point:
- **Correct** → one-sentence confirmation + one easily-missed detail worth knowing → release the next step.
- **Wrong** → name the exact spot in the screenshot that is wrong, explain why, give the minimal fix. Do not
  re-post the whole step.
- **Unreadable / missing key info** → say plainly "this shot does not show X, please re-capture with X in frame".
  Never guess from a blurry image and never pretend to have verified something you cannot see.

**d. Update the progress file** after each completed step (`progress/<course>.md`, see `record-sync.md`). For a
multi-step assignment, one line per step is enough.

**e. Never preview later steps.** If he asks "what's next", give the title only.

Failure handling:
- Multiple screenshots at once → acknowledge each one individually; do not look only at the last.
- He jumps ahead and sends step 4 evidence without step 3 → say which evidence is missing, without scolding,
  then continue from the right place.
- The screenshot proves the step failed → treat it as the valuable case it is: diagnose from what the screen
  shows (error text, missing signal, wrong pin), and give the smallest corrective action.

## Phase 3 — Produce the report

**Strict scope.** Include exactly:
- Task requirements
- Specification tables (truth table, function table, register map, module listing — whatever the task defines)
- Implementation approach
- Run results
- Item-by-item analysis of waveforms / logs / output
- Time spent per stage
- Reflections and takeaways

**Explicitly excluded:** platform introductions, design methodology essays, textbook-style "experiment
objectives", and summary tables that merely restate the task. A previous version of this kind of report was cut
from 20 pages to 16 by removing exactly this material.

**Data sources:** only the screenshots and logs the user actually supplied. Never invent run results, timings, or
waveforms. Anything unverified gets `【待补：xxx】` in red so he can fill it in.

**Naming:** apply `identity.filename_pattern` from the config. With `student_id` and `name` left empty the
pattern collapses to just the assignment name (`作业3.docx`). Ask the user for the ID and name if the
submission requires them and the config does not carry them; never guess either one.

**Formats:** produce what `deliverables.formats` specifies, plus `deliverables.submission_formats` when the
work is being handed in (normally DOCX for editing and PDF for submission).

Then follow `html-report-to-pdf-submit` for the HTML → DOCX → PDF conversion and the pre-delivery self-check.

## Phase 4 — Archive

1. Copy the deliverables into `deliverables.dir` (from the config), inside a per-course subfolder.
2. Write the report summary and the list of key screenshots into `summaries/` in the records repo.
3. Mark the assignment complete in the progress file, with the completion date and the total time spent.

## Pitfalls Seen In Practice

- The user describes himself as "not knowing how to use the tool". Provide guidance as click-level instructions,
  not conceptual explanation, until he asks for the concept.
- Lab screenshots must carry proof of success. A screenshot of an empty editor window is not evidence of a
  working circuit; say so and ask for the waveform or the log instead.
- Do not batch the report until the end without collecting evidence along the way — evidence that was never
  captured cannot be reconstructed, and fabricating it is not an option.
