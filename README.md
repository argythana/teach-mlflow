# Teach MLflow — from beginner to advanced

Tutorials and teaching material for MLflow, aimed at researchers and data scientists who know Python and ML but are new to tracking servers, model serving, and MLOps.

## Start the MLflow tracking server first

Every tutorial notebook in this repo assumes a local MLflow tracking server is already running. **Before opening any notebook**, start it in a separate terminal from the repo root:

```bash
mlflow ui --host 127.0.0.1 --port 8080
```

Leave it running. Then open the UI at <http://127.0.0.1:8080> and run the notebooks. Artifacts and run metadata will land in an `mlruns/` folder next to wherever the server was started — running it from the repo root keeps things tidy.

If a notebook cell calls `mlflow.set_tracking_uri("http://127.0.0.1:8080")` while the server is **not** running, logging calls will fail.

## Setup

Requires Python **3.14** and [`uv`](https://docs.astral.sh/uv/) for dependency management.

```bash
uv sync          # creates .venv/ and installs locked dependencies
```

`direnv` will auto-activate the venv via `.envrc`; otherwise `source .venv/bin/activate`.

## Layout

- `official_tutorials/` — upstream MLflow tutorial notebooks, annotated with prerequisites and steps missing from the official docs.

## References

- [MLflow documentation](https://mlflow.org/docs/latest/index.html)
- [MLflow GitHub](https://github.com/mlflow/mlflow)
