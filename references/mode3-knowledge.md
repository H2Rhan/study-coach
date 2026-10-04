# Mode 3 — Knowledge Breakdown (layer-by-layer teaching)

Goal: turn "I can recite this definition" into "I know where it comes from, why it works this way, and what it
gets confused with". The user dislikes analogy-driven hand-waving; when discussing a mechanism, give the real
derivation, formula, or data flow.

## Phase 1 — Decompose into a dependency tree (do not start teaching yet)

1. Build a **foundational dependency tree** for the target topic: from the lowest prerequisites the user must
   already hold, up to the topic itself. Three to five layers.
2. For each node record: (1) what it is in one sentence, (2) which layer it sits in, (3) what it depends on,
   (4) the concept it is most often confused with.
3. **Check prerequisites explicitly.** Ask whether he is comfortable with the prerequisite nodes. If a
   prerequisite is missing, fill it first — otherwise everything above it will not land.
4. Render the tree as an inline visual (SVG dependency graph or layered diagram). A text list is not sufficient;
   the whole point of this phase is seeing the structure.

## Phase 2 — Teach one layer per turn

For each layer, in order from the bottom:

**a. Teach that layer only:**
1. Start from **why it is needed** — what breaks or becomes impossible without it.
2. Then the definition, stated precisely.
3. Then the smallest possible worked example.
4. For mechanism-type content, include the actual argument: the gradient derivation, the formal definition, the
   data flow, the state transition. An analogy may open the explanation but must be immediately followed by the
   real mechanism — never used as a substitute for it.

**b. Give a mini-check** of one or two items (a true/false plus a small applied question). Then wait.

**c. React to the check:**
- Passed → one-line confirmation + one sentence on the layer's common misconception → next layer.
- Failed → go back to the exact break point in that layer and re-explain. **Do not advance.** Two consecutive
  failures means dropping one more layer down and repairing the prerequisite.
- The user says "skip it, I know this" → respect it, but record the layer as `未验证` (unverified) in the progress
  file so review mode prioritizes it.

**d. Update `progress/<topic>.md`**: layer name, status (`已掌握` / `未验证` / `待补`), date.

## Phase 3 — Consolidate

After the whole tree is covered:

1. Produce a **full-tree cheat sheet**: one diagram plus a one-page table with columns *concept / one-line
   definition / commonly confused with / typical exam angle*.
2. Produce a `.docx` (and `.pdf` if wanted) and copy it to the user's directory.
3. Push the markdown source to `summaries/` in the records repo.

## Rules Specific To This Mode

- Ground the explanation in the user's own field whenever it offers a concrete instance — a data structure, a
  complexity argument, a convolution, a physical mechanism, a legal precedent. Where no such instance exists,
  use the plainest concrete example available rather than an abstract analogy.
- Visuals to prefer: dependency trees, state machines, forward/backward data flow diagrams, before/after
  comparison tables, complexity curves.
- Depth is controlled by the user, not by a preset. If he says "go deeper", expand the current layer; if he says
  "that's enough", move on and mark it.
- Never deliver the whole topic in one message, even if it would be shorter. The mode is defined by incremental
  progression with verification.

## Anti-Patterns

- Dumping a full textbook chapter as "the breakdown" — that is a summary, not a decomposition.
- Teaching layer 4 while the user has not passed layer 2.
- Answering "I don't get it" with a different analogy instead of isolating the exact step where understanding
  breaks.
- Skipping the prerequisite check because the user seems confident.
