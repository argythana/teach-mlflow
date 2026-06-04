---
name: mlflow-tutorial-improve
description: >
  Use this skill when working inside this MLflow teaching repository to
  improve a tutorial notebook under `src/` (the `basics/`, `ml/`, or
  `gen_ai/` track) — expand,
  annotate, rewrite, draft a new section, restructure for flow, or
  clean up after a previous refactor — so it is friendlier for beginner
  data scientists and researchers. Trigger on prompts like "expand this
  MLflow section", "explain this MLflow concept better", "make this
  notebook beginner-friendly", "what context should we add to this
  cell", "why does this MLflow feature exist", "the logical flow here
  is broken", or "clean up the leftover trees / placeholder cells / old
  references". If the target notebook or cell is unclear, ask which one
  to edit after routing. Do NOT use it for general Python or ML
  tutorial writing outside this repo, for editing the upstream MLflow
  library itself, for non-tutorial docs in this repo (`README.md`,
  `CLAUDE.md`), or for non-teaching changes to the notebooks (file
  moves, dependency bumps, formatting, kernel metadata). For dependency
  work use `uv-deps`; for staging edits use `git-staging`; for the
  commit message use `commit-message`.
---

# MLflow tutorial improve

Editorial skill for this repo. Use it to improve an MLflow tutorial
notebook in the project's house style — beginner-friendly, concise, and
grounded in the problem each MLflow feature solves. "Improve" covers
expanding a section, annotating upstream content, restructuring for
logical flow, and cleaning up after earlier work — not just adding new
material.

## Audience

Researchers, data scientists, and CS students who already know Python
and ML but are new to MLflow, tracking servers, model serving, and
MLOps. They have probably been doing ML in single notebooks with no
experiment tracking. Assume zero MLflow knowledge; do not assume
production deployment experience.

## Editorial principles

Follow these in order of priority. If a draft violates one, prefer
trimming over justifying.

### 1. Lead with the problem, not the API

For every MLflow feature, the expansion answers **why** before **how**:

- What goes wrong without this feature? (lost experiments, untracked
  hyperparameters, "which pickle was the good one", broken handoffs.)
- What does it replace in the reader's current workflow? (a spreadsheet,
  filename conventions, asking a colleague.)
- What DS / MLOps / ML-system concern does it serve? — reproducibility,
  observability, collaboration, governance, deployment.

Only after the problem is named, show the API call.

### 2. Define terminology once, concisely

Define jargon the first time it appears. Prefer:

- a one-sentence definition, or
- a compact table when several related terms appear together (see the
  three-store table in `b_tracking_quickstart.ipynb`).

Do not redefine the same term in every section. Do not write a glossary
appendix — define terms where they are first used.

### 3. Add examples only when they teach something new

A second example must contrast with the first: a different store
backend, a parameter override, an error case, a registry promotion.
Variations that only relabel parameters belong on the cutting-room
floor.

### 4. Keep notebooks short

If an expansion pushes a notebook past one focused topic, split into a
new lettered notebook (`a_`, `b_`, `c_`, …) rather than letting one
notebook sprawl. Each notebook should be readable in one sitting.

### 5. Surface MLflow version drift

MLflow 3 changed several defaults (SQLite backend, registry available
out of the box, artifact-proxy URI). When a reader following older
blog posts or pre-3.x tutorials would be misled, add a short "what
changed" note. Do not write a full version-history dump — only flag
changes that affect the current step.

### 6. Refactor cleanly — a tutorial is not a changelog

When you fix a mistake, rename a convention, or restructure a section,
remove the old version with the same edit. The reader of this notebook
tomorrow should not have to reason about what the notebook used to look
like yesterday. Concretely:

- If a code change makes earlier output stale (e.g. switching
  `serialization_format` from `cloudpickle` to `skops` turns every
  `model.pkl` tree into a relic), update or delete every tree dump,
  table row, and prose reference that still shows the old artifact.
- If a refactor leaves placeholder code cells, orphan one-liners outside
  a `start_run`, or "TODO: add the real cell here" stubs, delete them
  or replace them with the missing real cell — do not ship a notebook
  whose downstream cells reference a variable the upstream cell never
  defines.
- If you change a convention (e.g. server cwd: repo root → `src/`),
  sweep every section that previously assumed the old convention and
  rewrite it; do not stack a new caveat on top of the old narrative.
- Duplicate tree dumps, redundant "after the Nth run" snapshots, and
  multiple slightly-different versions of the same example are noise.
  Keep one, the most useful, in the right place.
- Stale on-disk state (`mlflow.db`, `mlartifacts/`) left over from
  earlier conventions is per-developer junk; it is safe to delete and
  re-run, and the notebook should reflect the post-cleanup state, not
  the cumulative history.

The test: a fresh reader running the notebook end-to-end today should
get output that matches every tree, table, and snippet in the notebook
exactly. If any tree shows a file they won't produce, fix the tree (or
delete it).

### 7. Make code cells idempotent — re-running should not break the tutorial

A tutorial reader will re-run cells: to check the output, to recover
from a typo two cells later, to demo to a colleague, after restarting a
kernel. A cell that errors on the second run interrupts the learning
flow — the reader now has to debug *the tutorial* instead of the topic
it teaches.

Wherever a cell creates server-side state (an experiment, a registered
model, a database row), wrap the creation in a guard that turns the
"already exists" error into a no-op. Use the exception class MLflow
already raises so the reader sees the relevant error name in the
source:

```python
from mlflow.exceptions import RestException

try:
    mlflow.create_experiment(name=NAME, artifact_location=...)
except RestException as e:
    if "RESOURCE_ALREADY_EXISTS" not in str(e):
        raise
```

Concrete checklist:

- **Experiment creation** — guard `create_experiment` against
  `RESOURCE_ALREADY_EXISTS` (above pattern), or use
  `mlflow.set_experiment(name)` if you don't need `artifact_location`
  / tags.
- **Registered models** — `log_model(..., registered_model_name=...)`
  is already idempotent in the sense that it doesn't error; it appends
  a new version. If that's confusing, call out "version 2 on second
  run" in the surrounding prose so the reader doesn't think something
  broke.
- **Run contexts** — always use `with mlflow.start_run():`. Manual
  `start_run()` / `end_run()` pairs leak a `RUNNING` row on the next
  exception.
- **File writes** — `Path("...").mkdir(parents=True, exist_ok=True)`,
  `open(..., "w")` is fine if you intend to overwrite. Tutorial cells
  should not `raise FileExistsError` on the second run.
- **Side-effecting setup** — `mlflow.set_tracking_uri(...)`, env-var
  exports, `mlflow.set_experiment(...)` are all naturally idempotent;
  prefer them over operations that aren't.

The test: starting from a notebook that has been run once, Run All
again. Every cell should either succeed silently or show the *same*
output as the first run. No new exceptions.

### 8. Polish for readability — short lines, distinct concepts, no walls of text

A tutorial cell competes for the reader's attention against everything
else in their browser. Dense paragraphs with multiple sentences per
line slow scanning to a crawl; the reader gives up before reaching the
API call. Apply these rules to every prose cell longer than two
sentences:

- **Soft line breaks** between sentences inside the same paragraph.
  Each sentence on its own line. The paragraph still renders as one
  block, but the source reads like a script — and the rendered prose
  has visible breath marks.

  > **CommonMark gotcha — the breaks must be syntactically correct or
  > they do not render at all.** A bare `\n` between two non-empty
  > lines collapses to a single space in the rendered output: the
  > reader sees one continuous paragraph, the source looks broken to
  > anyone editing it. To get a visible `<br>`, you must end the
  > prior line with **two trailing spaces**, *then* the newline:
  >
  > ```
  > First sentence.  ← two trailing spaces here
  > Second sentence.
  > ```
  >
  > This is the single most common silent failure when polishing a
  > tutorial. If the rendered Jupyter cell shows two sentences on the
  > same line when the source has them on different lines, the
  > trailing spaces are missing.
- **One bullet per distinct sub-concept**, not one bullet per clause.
  If a bullet would run to four full lines of prose, it is probably
  two bullets.
- **`**Label:**` followed by a soft break** when a bullet (or paragraph)
  covers a distinct sub-case. The reader can skim the bold labels
  first, then drop into the body of the one they care about.
- **Convert run-on lists in prose to bulleted lists.**
  "It records the run id, start time, parameters, metrics, tags, status,
  and the user" → a bullet list of seven items.
- **Light verbosity reduction.** Cut parenthetical asides that the
  surrounding sentence already implies. Prefer declarative sentences
  over hedge-stacked ones ("a process-global piece of state on the
  client, and every subsequent `start_run()` reads from it until
  something else changes it" → split into two sentences).

What this is *not*:

- **Not a wholesale rewrite.** If a paragraph is already short and
  clear, leave it.
- **Not a stylistic tic.** `**Label:**` blocks should land on bullets
  that have genuinely distinct content, not every bullet.
- **Not formatting for its own sake.** The test is whether a beginner
  can scan the cell in ~10 seconds and know which sub-section to read
  in full.

### 9. Annotate the upstream relationship with inline bold callouts

When an addition relates to upstream content — correcting, supplementing,
or deliberately diverging from it — open the paragraph with one of four
**inline bold callouts**. Do not use them as heading prefixes. A
paragraph can carry at most one label; pick the one that most accurately
names the relationship.

| Label | When to use | Example |
|---|---|---|
| `**Bug in upstream tutorial:**` | Upstream code or claim is factually wrong or no longer runs (deprecated API, removed kwarg, incorrect statement). | Upstream's `mlflow.register_model(...)` snippet hardcodes a placeholder `run_id` that errors with `Run not found` on copy-paste. |
| `**Stale in upstream tutorial:**` | Upstream is out of date but not broken: defaults shifted in a new MLflow version, help text references retired behaviour, recommended-but-not-yet-default practices. | Upstream `--backend-store-uri` help says `./mlruns`; actual MLflow 3 default is `sqlite:///mlflow.db`. |
| `**Missing from upstream tutorial:**` | Upstream skips a prerequisite the reader needs for the code to run at all. The upstream code is fine *if* you do this first. | Upstream calls `mlflow.set_tracking_uri("http://127.0.0.1:5000")` without telling the reader to start the server first. |
| `**Diverges from upstream tutorial:**` | Upstream is fine, but this repo deliberately does it differently as a house policy. Name the policy briefly so the reader does not infer upstream is wrong. | Upstream uses `pip install mlflow`; this repo uses `uv add mlflow` because `pyproject.toml` + `uv.lock` are the single source of truth. |

Standalone topics — additions that have no upstream counterpart at all
(e.g. the `mlflow ui` vs `mlflow server` clarification in
`a_setup_mlflow.ipynb`) — get a plain `## <Topic>` heading with no
callout. Labeling them anything is performative.

Do not rewrite upstream prose. Leave the original markdown cells
recognizable and add new cells around them.

## House patterns

These patterns recur in `b_tracking_quickstart.ipynb` and should be
reused when they fit:

- **Comparison tables** for parallel concepts (e.g. backend / artifact
  / registry stores; tracking URI vs registry URI).
- **What changed in MLflow 3** callouts when defaults shifted.
- **Inspecting it (optional)** subsections with a one-liner shell or
  Python command the reader can run to peek at state (`sqlite3
  mlflow.db ".tables"`).
- **Overriding it** subsections showing the CLI flag or env var to
  customise the default, with one realistic alternative (Postgres,
  custom path) — not an exhaustive list.
- **For local learning, leaving the defaults alone is the right call**
  — give the reader permission to skip configuration rabbit holes.

## Workflow

1. Identify the section or concept to expand. Read the surrounding cells
   so the addition fits the flow.
2. Decide the upstream relationship of the addition (see principle 9):
   - **bug** → inline `**Bug in upstream tutorial:**` callout
   - **stale** → inline `**Stale in upstream tutorial:**` callout
   - **missing** → inline `**Missing from upstream tutorial:**` callout
   - **diverges** → inline `**Diverges from upstream tutorial:**` callout
   - **standalone topic** (no upstream counterpart) → plain `## <Topic>`
     heading, no callout
3. Draft the expansion in this order:
   - **Problem** — what breaks without it.
   - **Concept / definition** — one paragraph or table.
   - **Default behaviour in MLflow 3+** — the happy path.
   - **What changed / version note** — only if a stale tutorial would
     mislead the reader.
   - **Optional inspect / override** — one example each, not more.
4. Re-read the draft and cut anything that does not pass the "does this
   add value the reader cannot get from the official docs?" test.
5. Confirm the notebook still reads in one sitting. If not, propose a
   split into another lettered notebook.

## Anti-patterns

Stop and rewrite if the draft does any of these:

- Opens with an API call before establishing the problem.
- Repeats a definition already given earlier in the notebook.
- Includes a second example that does not contrast with the first.
- Treats MLflow as a black box ("just call this") without naming the
  DS/MLOps concern.
- Adds a "history of MLflow" paragraph unrelated to the current step.
- Inlines reference-style content that belongs in the official docs
  (full CLI flag listings, exhaustive API tables).
- Rewrites or paraphrases upstream cells instead of wrapping them.
- Edits notebook JSON metadata (kernelspec, execution counts,
  formatting) under the guise of "expansion". Those are not teaching
  changes and do not belong to this skill.
- Uses `MISSING FROM THE OFFICIAL TUTORIAL` as a heading prefix on
  additions. That convention is retired in favour of the four
  inline-bold callouts in principle 9. Use a plain heading for
  standalone topics; use an inline callout for upstream-relationship
  signal.
- Stacks multiple upstream-relationship callouts on one paragraph.
  Pick the single label that most accurately names the relationship.
- Leaves stale artifacts in place after a refactor — duplicate tree
  dumps, placeholder code cells with "TODO" comments, orphan one-liners
  outside any `start_run`, prose that still references a `.pkl` file
  after switching to `skops`, caveats stacked on top of an outdated
  narrative, or downstream cells that reference variables an upstream
  cell no longer defines. See principle 6 — a tutorial is not a
  changelog.
- Leaves a cell that raises on the second `Run All` — bare
  `mlflow.create_experiment(...)` calls that hit
  `RESOURCE_ALREADY_EXISTS` on re-run, file writes that fail with
  `FileExistsError`, manual `mlflow.start_run()` without `with` that
  leaks a `RUNNING` row on the next exception. See principle 7 — every
  cell should be safe to run twice.
- Ships prose-heavy cells as wall-of-text paragraphs: 60+ word sentences,
  comma-separated lists embedded in running prose, multiple distinct
  sub-topics jammed into the same bullet, no bold labels for skim. See
  principle 8 — the reader needs visible structure to navigate.

## Out of scope

- Editing the upstream MLflow library or filing issues against it.
- Generic Python or scikit-learn tutorials unrelated to MLflow.
- Adding dependencies (use `uv-deps`).
- Staging and committing the resulting edits (use `git-staging` and
  `commit-message`).
- Setting up CI, deployment, or non-teaching infrastructure.
