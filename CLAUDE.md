# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This is a **learning/teaching repository** for MLflow, not a library or service. The goal is to build tutorials and explanations that take a reader from "I know Python and ML" to advanced MLflow / MLOps topics (model tracking, registry, serving). The target audience is researchers and data scientists who are *not* familiar with running servers, model serving, or MLOps. Source material is meant to start from the official MLflow docs/tutorials and be augmented where they are unclear or missing steps. Treat the working `tracking_quickstart.ipynb` cell `MISSING FROM THE OFFICIAL TUTORIAL` annotation as the canonical example of how to add value on top of upstream material.

## Environment

- Python **3.14** (`pyproject.toml` pins `requires-python = ">=3.14"`).
- A local venv lives at `.venv/`. **direnv** activates it via `.envrc` (`source ./.venv/bin/activate`); if direnv is not loaded, activate manually with `source .venv/bin/activate`.
- **Dependency management uses `uv` exclusively. Do not use `pip`** — do not bootstrap it with `ensurepip`, do not seed the venv with `uv venv --seed`, do not run `pip install` or `uv pip install`. All package changes go through the uv project workflow so `pyproject.toml` and `uv.lock` stay the single source of truth.
  - Add a dependency: `uv add <package>` (use `--dev` for dev-only tools).
  - Remove: `uv remove <package>`.
  - Reproduce the environment on a fresh checkout: `uv sync`.
  - Commit `uv.lock` along with `pyproject.toml` changes.
- The venv is currently **bare** (no `mlflow`, no `jupyter`). The first `uv add` will populate the empty `dependencies = []` in `pyproject.toml`, generate `uv.lock`, and sync `.venv/`.

## Running the MLflow tutorials

The notebooks assume a **local MLflow tracking server is already running**. Before executing any cell that calls `mlflow.set_tracking_uri("http://127.0.0.1:8080")`, start the server in a separate terminal:

```bash
mlflow ui --host 127.0.0.1 --port 8080
```

This creates an `mlruns/` folder relative to the directory where the server was started — start it from the repo root so artifacts land in a predictable place. The official upstream quickstart **omits this step**; surfacing prerequisites like this is part of the teaching value-add of this repo.

## Repository layout

- `official_tutorials/` — verbatim or near-verbatim notebooks from the MLflow docs, with added markdown cells filling in missing setup steps. Keep upstream content recognizable; annotate additions clearly (e.g. `### MISSING FROM THE OFFICIAL TUTORIAL:`).
- `README.md` — currently a draft outline of audience / difficulty / references.
- `pyproject.toml` — minimal project metadata; dependencies still need to be filled in as tutorials grow.
