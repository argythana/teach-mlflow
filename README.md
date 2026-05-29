# Teach MLflow — from beginner to advanced

Tutorials and teaching material for MLflow, aimed at researchers and data scientists who know Python and ML but are new to tracking servers, model serving, and MLOps.

MLflow has evolved rapidly and gained wide adoption. Since version 3 it has grown into a platform for tracking both traditional ML experiments and modern AI / LLM workflows.

Most ML courses, meanwhile, teach algorithms and their metrics as standalone topics and skip the reproducibility, observability, and monitoring that scientific research and production ML systems depend on.

MLflow is not taught at any Computer Science university in Greece, even though it is essential for data scientists. The goal of this repo is to provide beginner-friendly, up-to-date learning resources that help fill that gap.

## The tutorials

Notebooks live in `src/official_tutorials/` and are prefixed `a_`, `b_`, `c_`, … so the intended reading order is obvious from `ls`. Each one stays close to the official MLflow material but adds the prerequisites, terminology, and "why this feature exists" context the upstream docs assume or skip.

**Getting started** (local server on port `5000`):

- `a_setup_mlflow` — what MLflow solves; `mlflow ui` vs `mlflow server`; connecting a notebook to a tracking server.
- `b_tracking_quickstart` — log a model, parameters, and metrics; the three stores (backend / artifact / registry); safe serialization with `skops`.
- `c_hyperparameter_tuning` — an Optuna sweep with parent/child runs, and a first look at the model registry.

**Advanced** (local server on port `5001`):

- `d_logging_plots` — log EDA and diagnostic figures across a sweep with `mlflow.log_figure`.
- `e_logging_callbacks` — XGBoost + Optuna callbacks; parent-run metric history vs stdout heartbeats.
- `f_model_evaluation` — `mlflow.evaluate()`, custom metrics, and validation gates (CI for models).
- `g_model_registry` — versions, `@champion` / `@challenger` aliases, the promotion lifecycle, and rollback.
- `h_model_serving` — serve a registered model over REST with `mlflow models serve`; the `/invocations` contract, signature enforcement, and the container path.

That completes the traditional-ML MLOps spine (tracking → evaluation → registry → serving). A GenAI / LLM track is the planned Part 2.

## Start the MLflow tracking server first

Every notebook assumes a local MLflow tracking server is already running. **Before opening a notebook**, start it in a separate terminal from the repo root, on the port that notebook expects — the getting-started notebooks use `5000`, the advanced ones use `5001`, and the first cell of each notebook states which:

```bash
mlflow ui --host 127.0.0.1 --port 5000   # use 5001 for d_ onward
```

Leave it running and open the UI at the matching address (e.g. <http://127.0.0.1:5000>). In MLflow 3 this creates a `mlflow.db` (the SQLite backend store) and an `mlartifacts/` directory next to wherever you started the server — running it from the repo root keeps them tidy. Both are per-developer runtime state and are gitignored.

If a notebook cell calls `mlflow.set_tracking_uri("http://127.0.0.1:<port>")` while no server is listening on that port, the logging calls will fail.

## Setup

Requires Python **3.14** and [`uv`](https://docs.astral.sh/uv/) for dependency management.

```bash
uv sync          # creates .venv/ and installs locked dependencies
```

`direnv` auto-activates the venv via `.envrc`; otherwise `source .venv/bin/activate`.

## References

- [MLflow documentation](https://mlflow.org/docs/latest/index.html)
- [MLflow GitHub](https://github.com/mlflow/mlflow)
