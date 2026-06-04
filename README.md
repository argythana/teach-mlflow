# Teach MLflow — from beginner to advanced

Tutorials and teaching material for MLflow, aimed at researchers and data scientists who know Python and ML but are new to tracking servers, model serving, and MLOps.

MLflow has evolved rapidly and gained wide adoption. Since version 3 it has grown into a platform for tracking both traditional ML experiments and modern AI / LLM workflows.

Most ML courses, meanwhile, teach algorithms and their metrics as standalone topics and skip the reproducibility, observability, and monitoring that scientific research and production ML systems depend on.

MLflow is not taught at any Computer Science university in Greece, even though it is essential for data scientists. The goal of this repo is to provide beginner-friendly, up-to-date learning resources that help fill that gap.

## The tutorials

Notebooks are grouped by track. Each folder is prefixed `a_`, `b_`, `c_`, … so the intended reading order is obvious from `ls`. Each one stays close to the official MLflow material but adds the prerequisites, terminology, and "why this feature exists" context the upstream docs assume or skip.

**`basics/` — shared foundations** (local server on port `5000`), the starting point for either track:

- `a_setup_mlflow` — what MLflow solves; `mlflow ui` vs `mlflow server`; connecting a notebook to a tracking server.
- `b_tracking_quickstart` — log a model, parameters, and metrics; the three stores (backend / artifact / registry); safe serialization with `skops`.

**`ml/` — traditional-ML track** (local server on port `5001`):

- `a_hyperparameter_tuning` — an Optuna sweep with parent/child runs, and a first look at the model registry.
- `b_logging_plots` — log EDA and diagnostic figures across a sweep with `mlflow.log_figure`.
- `c_logging_callbacks` — XGBoost + Optuna callbacks; parent-run metric history vs stdout heartbeats.
- `d_model_evaluation` — `mlflow.evaluate()`, custom metrics, and validation gates (CI for models).
- `e_model_registry` — versions, `@champion` / `@challenger` aliases, the promotion lifecycle, and rollback.
- `f_model_serving` — serve a registered model over REST with `mlflow models serve`; the `/invocations` contract, signature enforcement, and the container path.
- `g_dataset_logging` — `mlflow.data` + `log_input` for dataset lineage (raw vs engineered features, digests).
- `h_system_metrics` — `system/*` resource observability (CPU / RAM / GPU) under a heavy training load.
- `i_capstone_end_to_end` — one model through the full lifecycle: feature-engineer → tune → evaluate → gate → register → serve.

That completes the traditional-ML MLOps spine (tracking → evaluation → registry → serving).

**`gen_ai/` — GenAI / LLM track** (planned): tracing, LLM-as-judge evaluation, and the prompt registry — this is where the MLflow **Traces** tab lights up. See `roadmap/` for the plan.

## Start the MLflow tracking server first

Every notebook assumes a local MLflow tracking server is already running. **Before opening a notebook**, start it in a separate terminal from the repo root, on the port that notebook expects — the `basics/` notebooks use `5000`, the `ml/` track uses `5001`, and the first cell of each notebook states which:

```bash
mlflow ui --host 127.0.0.1 --port 5000   # use 5001 for the ml/ track
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
