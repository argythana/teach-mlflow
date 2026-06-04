# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This is a **learning/teaching repository** for MLflow, not a library or service. The goal is to build tutorials and explanations that take a reader from "I know Python and ML" to advanced MLflow / MLOps topics (tracking, registry, serving). The target audience is researchers and data scientists who are *not* familiar with running servers, model serving, or MLOps — including students at universities that do not teach MLflow.

Source material starts from the official MLflow docs/tutorials and is augmented where they are unclear, skip a step, or fail to motivate why the feature exists. Treat `src/basics/b_tracking_quickstart.ipynb` as the canonical example of how to add value on top of upstream material — in particular the `## MISSING FROM THE OFFICIAL TUTORIAL` section and the "MLflow Default Database and Registry store URI" deep-dive (three-store table, "what changed in MLflow 3", problem→feature framing).

## Teaching philosophy

When adding to, expanding, restructuring, or cleaning up a tutorial, follow these editorial principles. The `mlflow-tutorial-improve` skill at `.claude/skills/mlflow-tutorial-improve/` codifies them in more detail.

- **Explain terminology, but stay concise.** Define jargon the first time it appears (e.g. *backend store*, *artifact store*, *registered model*, *pyfunc*). One short paragraph or a table, not a wall of text.
- **Motivate every feature with the problem it solves.** Before showing *how* to call an API, explain *why* a data scientist or ML system would need it. What goes wrong without it? What does it replace (notes in a spreadsheet, ad-hoc pickle files, "ask the author")?
- **Connect to Data Science / MLOps / ML systems context.** Frame each MLflow feature in terms of reproducibility, observability, collaboration, deployment, or governance — the concerns that distinguish research/production ML from a one-off notebook.
- **Add examples only when they add value.** A second example must teach something the first did not (an edge case, an override, a contrast). Do not pad notebooks with redundant variations.
- **Keep notebooks short.** A long notebook is a sign that two topics have been mashed together — split it (e.g. `a_setup_mlflow` and `b_tracking_quickstart`).
- **Surface MLflow version drift.** MLflow 3 changed several defaults (e.g. `sqlite:///mlflow.db` backend, registry enabled by default). Call these out when a reader following an older blog post or tutorial would be confused.
- **Annotate additions clearly.** Use markdown headings like `## MISSING FROM THE OFFICIAL TUTORIAL` so a reader can tell upstream content from this repo's value-add.
- **Keep upstream content recognizable.** Do not rewrite official tutorials — wrap them with prerequisites, context, and follow-ups.

## Environment

- Python **3.14** (`pyproject.toml` pins `requires-python = ">=3.14"`).
- A local venv lives at `.venv/`. **direnv** activates it via `.envrc` (`source ./.venv/bin/activate`); if direnv is not loaded, activate manually with `source .venv/bin/activate`.
- **Dependency management uses `uv` exclusively. Do not use `pip`** — do not bootstrap it with `ensurepip`, do not seed the venv with `uv venv --seed`, do not run `pip install` or `uv pip install`. All package changes go through the uv project workflow so `pyproject.toml` and `uv.lock` stay the single source of truth.
  - Add a dependency: `uv add <package>` (use `--dev` for dev-only tools).
  - Remove: `uv remove <package>`.
  - Reproduce the environment on a fresh checkout: `uv sync`.
  - Commit `uv.lock` along with `pyproject.toml` changes.

## Running the MLflow tutorials

The notebooks assume a **local MLflow tracking server is already running**. Before executing any cell that calls `mlflow.set_tracking_uri("http://127.0.0.1:5000")`, start the server in a separate terminal from the repo root:

```bash
mlflow ui --host 127.0.0.1 --port 5000
```

In MLflow 3+ this creates `mlflow.db` (SQLite backend store) and an `mlartifacts/` directory in the cwd — start the server from the repo root so these land in a predictable place. Both are per-developer runtime state and are gitignored. The official upstream quickstart **omits the "start the server first" step**; surfacing prerequisites like this is part of the teaching value-add of this repo.

## Repository layout

- `src/` — adapted MLflow tutorial notebooks, grouped by track and ordered with `a_`, `b_`, `c_` prefixes so the intended reading sequence is obvious from `ls`. Each notebook stays close to the upstream original but adds prerequisites, terminology, and "why this feature exists" context per the [Teaching philosophy](#teaching-philosophy) above.
  - `src/basics/` — track-agnostic foundations both tracks build on (`a_setup_mlflow`, `b_tracking_quickstart`).
  - `src/ml/` — the traditional-ML track (`a_hyperparameter_tuning` … `i_capstone_end_to_end`): tuning, plots, evaluation, registry, serving, dataset logging, system metrics, capstone.
  - `src/gen_ai/` — the GenAI / LLM track (tracing, LLM-as-judge evaluation, prompt registry). In progress.
- `roadmap/` — the master roadmap summary (`roadmap.md`) and the build-out plan (`plan.md`).
- `README.md` — audience, motivation, and setup for readers of the repo.
- `pyproject.toml` / `uv.lock` — dependencies grow as tutorials cover more MLflow features (`mlflow`, `jupyter`, `scikit-learn`, `skops`, `optuna`, …).
- `.claude/skills/mlflow-tutorial-improve/` — editorial skill for expanding, restructuring, and cleaning up upstream tutorials in the project's house style.
