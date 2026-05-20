---
name: mlflow-tutorial-expand
description: >
  Use this skill when working inside this MLflow teaching repository
  (`src/official_tutorials/`) to expand, annotate, or rewrite a section
  of an official MLflow tutorial notebook so it is friendlier for
  beginner data scientists and researchers. Trigger on prompts like
  "expand this section", "explain this MLflow concept better", "make
  this beginner-friendly", "what context should we add here", "why does
  this MLflow feature exist", or "add a MISSING FROM THE OFFICIAL
  TUTORIAL section about X". Do NOT use it for general Python tutorial
  writing outside this repo, for editing the upstream MLflow library
  itself, for adding new code examples unrelated to MLflow features, or
  for non-teaching refactors of the notebooks (file moves, dependency
  bumps, formatting). For dependency work use `uv-deps`; for staging the
  resulting edits use `git-staging`.
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

### 6. Annotate additions, preserve upstream

- Use `## MISSING FROM THE OFFICIAL TUTORIAL` for prerequisite steps
  upstream skipped (e.g. starting the server, picking a port).
- Use a normal `## <Concept>` heading for conceptual deep-dives that
  expand on what upstream mentions in passing.
- Do not rewrite upstream prose. Leave the original markdown cells
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
2. Decide whether this is a **prerequisite gap** (`MISSING FROM THE
   OFFICIAL TUTORIAL`) or a **conceptual deep-dive** (regular heading).
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

## Out of scope

- Editing the upstream MLflow library or filing issues against it.
- Generic Python or scikit-learn tutorials unrelated to MLflow.
- Adding dependencies (use `uv-deps`).
- Staging and committing the resulting edits (use `git-staging` and
  `commit-message`).
- Setting up CI, deployment, or non-teaching infrastructure.
