---
name: mlflow-tutorial-expand
description: >
  Use this skill when working inside this MLflow teaching repository to
  expand, annotate, rewrite, or draft a section — or a whole new
  notebook — of an MLflow tutorial under `src/official_tutorials/` so
  it is friendlier for beginner data scientists and researchers.
  Trigger on prompts like "expand this MLflow section", "explain this
  MLflow concept better", "make this notebook beginner-friendly", "what
  context should we add to this cell", or "why does this MLflow feature
  exist". If the target notebook or cell is unclear, ask which one to
  edit after routing. Do NOT use it for general Python or ML tutorial
  writing outside this repo, for editing the upstream MLflow library
  itself, for non-tutorial docs in this repo (`README.md`, `CLAUDE.md`),
  or for non-teaching changes to the notebooks (file moves, dependency
  bumps, formatting, kernel metadata). For dependency work use
  `uv-deps`; for staging edits use `git-staging`; for the commit message
  use `commit-message`.
---

# MLflow tutorial expand

Editorial skill for this repo. Use it to expand a section of an MLflow
tutorial notebook in the project's house style — beginner-friendly,
concise, and grounded in the problem each MLflow feature solves.

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

### 6. Annotate the upstream relationship with inline bold callouts

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
2. Decide the upstream relationship of the addition (see principle 6):
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
  inline-bold callouts in principle 6. Use a plain heading for
  standalone topics; use an inline callout for upstream-relationship
  signal.
- Stacks multiple upstream-relationship callouts on one paragraph.
  Pick the single label that most accurately names the relationship.

## Out of scope

- Editing the upstream MLflow library or filing issues against it.
- Generic Python or scikit-learn tutorials unrelated to MLflow.
- Adding dependencies (use `uv-deps`).
- Staging and committing the resulting edits (use `git-staging` and
  `commit-message`).
- Setting up CI, deployment, or non-teaching infrastructure.
