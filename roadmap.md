# Tutorial roadmap

This file plans the tutorials in this repo and tracks what's done. It was written after a
survey of the official MLflow 3 docs, tutorial tracks, and the `mlflow/mlflow` GitHub
examples (June 2026, MLflow ~3.12). Treat it as a living document — update it as notebooks
land.

## Where the repo stands

| # | Notebook | Topic | Level | Status |
|---|----------|-------|-------|--------|
| a | `a_setup_mlflow` | Install, start the tracking server, first run | beginner | ✅ done |
| b | `b_tracking_quickstart` | Manual tracking: params, metrics, `log_model` | beginner | ✅ done |
| c | `c_hyperparameter_tuning` | Search + child runs | intermediate | ✅ done |
| d | `d_logging_plots` | Logging figures as artifacts | intermediate | ✅ done |
| e | `e_logging_callbacks` | Autolog-style callbacks (XGBoost) | advanced | ✅ done |
| f | `f_model_evaluation` | `mlflow.models.evaluate()`, custom metrics, validation gates | advanced | ✅ done |
| g | `g_model_registry` | Versions, aliases, promotion gate, rollback, governance | advanced | ✅ done |
| h | `h_model_serving` | `mlflow models serve`, `/invocations`, Docker path | advanced | ✅ done |
| i | `i_capstone_end_to_end` | One model through the full lifecycle | advanced | ⬜ **next** |

The traditional-ML MLOps spine is now built end to end: **track** (`b`–`e`) → **evaluate &
gate** (`f`) → **register & promote** (`g`) → **serve** (`h`). What remains is the
**autologging backfill** into existing notebooks (see "Autolog: backfill into existing
notebooks") and the **capstone** that runs *one* model through the whole spine on *one*
dataset.

## TODO / backlog (at a glance)

The actionable list. Details live in the sections below.

- [ ] **`e_` XGBoost autolog aside** — the last autolog backfill (one paragraph; see the autolog table).
- [ ] **`i_capstone_end_to_end`** — build it. Bundles three sub-sections: the lifecycle chain, **system metrics under load** (GPU/RAM), and **dataset logging** (raw vs engineered features).
- [ ] **`uv add pynvml`** — needed for the capstone's `system/gpu_*` metrics (GPU present, lib not installed). `uv add shap` is optional (richer `evaluate()` artifacts).
- [ ] **Decide:** dataset logging as a *capstone section* vs its **own short notebook** — it has standalone value; the capstone is already carrying a lot.
- [ ] **Optional — enhance `c_`'s autolog aside:** record that there is **no native MLflow autolog for Optuna**, and that `optuna_integration.MLflowCallback` is **deprecated** (4.9.0 → removal 6.0.0). (Researched June 2026; see the Optuna note under the autolog section.)
- [ ] **Optional — `h_` backfill:** add the `mlflow.models.predict()` pre-serve smoke test.

## The gap we're filling (still true)

The official MLflow material teaches each downstream feature on its own page, each with a
*different toy dataset and model* (iris here, wine-quality there, diabetes elsewhere). There
is **no single upstream tutorial** that follows one model through
train → evaluate → register → promote → serve. Our value-add is the **narrative thread** that
ties the existing APIs into one lifecycle, on one dataset (California housing +
RandomForest/XGBoost, for continuity with `d_`–`h_`).

## Guiding decisions (still in force)

- **Keep notebooks short and single-topic** (per CLAUDE.md). The capstone is the only one
  that combines everything, and it does so by *reusing* concepts, not re-teaching them.
- **Aliases, not stages.** MLflow 3 deprecated stage transitions. `g_` already teaches
  `models:/<name>@<alias>` with the deprecated-Stages contrast; `h_` serves the alias. The
  capstone follows suit.
- **Advanced notebooks use port 5001** for the tracking server; `h_` adds **5002** for the
  model server. The capstone reuses both.

---

## Coverage check: what `g_` and `h_` actually shipped

Both notebooks (already on `main`) match the plan closely. Recorded here so the roadmap
reflects reality, with the small deltas called out.

### `g_model_registry` — matches plan
Shipped: train + `register_model` (append-only versions) → `@champion` alias → `@challenger`
candidate → promotion gate (RMSE compare; defers the formal `validate_evaluation_results`
gate to `f_`) → rollback via one alias move → two-level tags + descriptions → `search_model_versions`
inspection and the "aliases live on the registered model, not the version rows" gotcha. Also
includes the **deprecated-Stages contrast table** and the **MLflow 3 LoggedModel
(`models:/m-<hash>`)** call-out.

**Delta vs plan:** the **autolog section we'd decided to fold in here was not included** — the
notebook uses only `scikit-learn` + `mlflow` and adds no `mlflow.sklearn.autolog()` content.
See "Autolog: backfill into existing notebooks" below (it landed in `b_` instead).

### `h_model_serving` — matches plan
Shipped: the problem framing (`load_model` only serves Python callers) → `mlflow models
serve` (FastAPI/uvicorn) → the serve command with `MLFLOW_TRACKING_URI` + `--env-manager
local` and the reproducibility trade-off → the `/invocations` contract
(`dataframe_split`/`dataframe_records`/`inputs`/`instances`, `{"predictions": […]}`) →
REST-vs-in-process equivalence check → `/health` + signature-enforcement guardrail (400 /
`SCHEMA_ENFORCEMENT_FAILED`) → `build-docker` container path → "promotion reaches the endpoint"
(alias resolved at load time, restart/webhook to pick up) → managed deployment targets.

**Deltas vs plan (minor, optional backfill):**
- The **`mlflow.models.predict()` pre-serve smoke test** (validate a model in an isolated env
  before standing up a server) was not included. Worth a short Step if we ever revise `h_`.
- No **MLServer-deprecation** note — but `h_` never teaches `--enable-mlserver`, so this is moot.

Neither delta is blocking. Capture them as possible touch-ups, not rework.

---

## Autolog: backfill into existing notebooks (planned)

Autolog is **too thin and too overlapping with `b_`/`c_` to be its own notebook** — and it's a
poor fit for a standalone because it's fundamentally an *alternative to logging you already
teach*. So the plan is to **backfill autolog as short, well-placed sections into the existing
notebooks**, each attached to the manual technique it replaces. This keeps every notebook
single-topic while teaching the one-line alternative exactly where the contrast lands.

The material splits cleanly across three existing notebooks:

| Add to | Section | Net-new content (~2–4 cells each) |
|---|---|---|
| **`b_tracking_quickstart`** ✅ **done** | "The one-line alternative: `mlflow.autolog()`" | Added after the skops section: `mlflow.sklearn.autolog()` capturing the same params + metrics + model + **signature** automatically, a manual-vs-autolog comparison table, the three gotchas (**`log_input_examples=False`**, **reverts to `cloudpickle`** — losing the notebook's skops safety — and surprise artifacts), universal-vs-flavor precedence, and a bridge to `c_`. Also normalized `b_` from `nbformat_minor` 2 → 5. *(Structure validated; not yet executed against a live server.)* |
| **`c_hyperparameter_tuning`** ✅ **done** | "Aside: `autolog` does the parent/child wiring — for scikit-learn search" | Added before Next steps: an aside contrasting the notebook's hand-wired **Optuna** loop (nested runs, per-trial `log_*`, manual best-run promotion) with `mlflow.sklearn.autolog()` on `GridSearchCV`, which builds the parent (`best_*`, `best_cv_score`, `training_*`, `cv_results.csv`) and child runs automatically via **`max_tuning_runs`** (default 5; `None` = all). Honest scope note: auto-grouping is sklearn-search-only — Optuna isn't a sklearn estimator, so the manual approach stays; plus the cloudpickle-vs-skops caveat. *(Verified live: parent + 3 of 4 combos as child runs.)* |
| **`e_logging_callbacks`** | one-paragraph aside | `e_` already does XGBoost callbacks; note that `mlflow.xgboost.autolog()` captures **per-iteration metrics + feature-importance plots** for free, and when you'd still reach for explicit callbacks. Cross-link, don't re-teach. |

**Recommended sequencing:** the **`b_`** and **`c_`** sections are **done**; the **`e_`**
XGBoost autolog aside is the only autolog backfill left. Each is independent and lands in its
own small commit.

**Version-drift to surface in the `b_` section:** MLflow 3 logs models as first-class
**LoggedModel** entities; `log_datasets=True` and `log_models=True` are defaults;
`log_input_examples=False` is *not*. Sources: autolog overview
<https://mlflow.org/docs/latest/ml/tracking/autolog/>, `mlflow.sklearn`/`mlflow.xgboost` API
refs.

**Optuna + MLflow — there is no native autolog (researched June 2026).** Worth recording,
since readers expect an `mlflow.optuna.autolog()` by analogy with sklearn/xgboost:
- `mlflow.autolog()` does **not** support Optuna — it isn't in the supported-flavor list
  (sklearn, xgboost, lightgbm, keras/tf, pytorch, spark, statsmodels, paddle). No
  `mlflow.optuna.autolog()` exists. The only autolog *additions* in 2024–2026 are GenAI/
  tracing flavors.
- The real integration is **Optuna-side**: `optuna_integration.MLflowCallback` (the package
  split out of core Optuna — install `optuna-integration[mlflow]`, import
  `from optuna_integration import MLflowCallback`; `optuna.integration.mlflow` is now a
  re-export shim). It creates **one flat run per trial by default**; nest via
  `mlflow_kwargs={"nested": True}`. **It is deprecated** — `@deprecated_class("4.9.0", "6.0.0")`
  — so don't anchor new work on it.
- MLflow's official Optuna tutorial uses **manual nested runs** — exactly what `c_` does. So
  `c_`'s aside is accurate; the only enhancement worth making is to *state* this non-existence
  explicitly (see the TODO). Sources: autolog flavor list
  <https://mlflow.org/docs/latest/ml/tracking/autolog/>; `MLflowCallback` ref
  <https://optuna-integration.readthedocs.io/en/stable/reference/generated/optuna_integration.MLflowCallback.html>;
  MLflow Optuna tutorial
  <https://mlflow.org/docs/latest/ml/traditional-ml/tutorials/hyperparameter-tuning/>.

---

## i_capstone_end_to_end (next — advanced)

**Purpose.** One realistic, continuous workflow on **one** dataset/model that closes the loop
the official docs leave fragmented. This is the notebook that makes the whole repo cohere.

**The chain (each step reuses an earlier notebook's concept, doesn't re-teach it):**
1. **Feature-engineer** the raw data and **log both the raw and engineered datasets**
   (`mlflow.log_input`) so the run records what the model actually saw — *new* material; see
   the "Dataset logging" section below.
2. Tune a few candidate models with child runs (`c_`) — optionally via `autolog()`,
   cross-linking rather than re-teaching it.
3. `mlflow.models.evaluate()` to pick the best by held-out RMSE/R² (`f_`).
4. Gate the winner with `validate_evaluation_results` against a baseline (`f_`).
5. `register_model(...)` the model that passed → assign `@champion`; keep runner-up as
   `@challenger` (`g_`).
6. Load `models:/...@champion` and sanity-check (`g_`).
7. `mlflow models serve` + curl a real prediction (`h_`).

Plus two cross-cutting sub-sections layered onto the run: **dataset logging** (below) and
**system metrics under load** (below).

**Design constraints:**
- Keep it a *capstone*, not a re-teach: link back to `c_`/`f_`/`g_`/`h_` for the "why," and
  spend the prose on the **decisions** that connect the steps ("select the best, gate it,
  promote *that one*, serve it"). The official material never makes those decisions explicit
  because evaluation is siloed from registry/serving.
- Acknowledge the official toy framing once (wine-quality ElasticNet / iris) and explain why
  we use California housing + RandomForest/XGBoost instead (continuity + a richer target).
- This is the first notebook that exercises **both** extra processes at once (tracking on
  5001, serving on 5002) — spell out the terminal setup, as `h_` does.

### Dataset logging — raw vs engineered features (capstone section)

The capstone is the first notebook to do real **feature engineering**, which is exactly the
case that motivates **dataset tracking**: once the columns the model trains on differ from the
raw data, "which data + which features produced this model?" is no longer answerable from the
run's params and metrics alone. `mlflow.data` + `mlflow.log_input` record that lineage.

**The problem it solves:** reproducibility and lineage. A run that trains on a *transformed*
frame should record both the **raw source** (provenance) and the **engineered feature set**
(what the model actually saw) — so a reader can reconstruct or audit the exact inputs.

**API:**
- Build a dataset object: `mlflow.data.from_pandas(df, source=..., name=..., targets="...")`
  (also `from_numpy`, `from_spark`, …). `source` is the lineage pointer (file/URL/Delta);
  `name` is the UI label; `targets` names the label column. Each dataset gets a `schema`
  (column types), a `profile` (row/element counts), and a `digest` (content fingerprint).
- Attach it to the run: `mlflow.log_input(dataset, context="training", tags={...})`.
  `context` is a free-form label (`"raw_source"`, `"training"`, `"validation"`, `"testing"`,
  `"evaluation"`). **Multiple `log_input` calls per run are the norm** — one per dataset.

**The raw + engineered pattern (the teaching core):**
```python
raw_ds = mlflow.data.from_pandas(raw_df, source=RAW_URL, name="ca-housing-raw", targets="target")
eng_df = feature_engineer(raw_df)                  # raw 8 features -> engineered N features
eng_ds = mlflow.data.from_pandas(eng_df, source=RAW_URL, name="ca-housing-engineered-v1",
                                 targets="target")
with mlflow.start_run():
    mlflow.log_input(raw_ds, context="raw_source")
    mlflow.log_input(eng_ds, context="training", tags={"feature_set": "v1", "n_features": "N"})
    # model.fit(eng_df.drop(columns="target"), eng_df["target"])
```

**Interactions / contrasts to teach:**
- **Autolog vs manual.** `log_datasets=True` (sklearn/xgboost autolog default) logs whatever
  `X`/`y` reaches `.fit()` — for a `Pipeline` that's typically the **raw input, with a weak/absent
  source**. The manual `log_input` of the engineered frame is what records the *transformed*
  features with a real `name`/`source`/`digest`. So: autolog is convenient; the manual call is
  what captures the engineered feature set properly. (Can do both; explain the difference.)
- **`evaluate(data=...)`** accepts an `mlflow.data.Dataset`, but it records dataset metadata to
  the `mlflow.datasets` *tag* rather than calling `log_input` — so still `log_input` the eval
  set if you want it in the run's "Datasets" UI panel.
- **Digest gotcha (teachable):** the pandas digest is an 8-char MD5 over the first **10 000**
  rows + row count + column names — a cheap fingerprint, not a full-content hash. Good for
  spotting "same data across runs" / train-serve skew, not a cryptographic guarantee.

**Storage gotcha:** MLflow logs dataset **metadata + source reference + digest, not the full
data**. To reload you go through `source.load()`, so pass a *real* `source` or you log a
dataset you can't re-materialize. `MetaDataset` is the explicit metadata-only variant.

**Dependencies:** none beyond `mlflow` + pandas (already present) for the `from_pandas` path.

**Open decision (see TODO):** keep this as a capstone section, or split into its own short
notebook. It has clean standalone value, and the capstone is already carrying the lifecycle
chain + system metrics. Leaning toward a capstone section so it stays tied to the
feature-engineering moment that motivates it — but flagged for a call.

**Sources:** dataset tracking guide — <https://mlflow.org/docs/latest/ml/dataset/>;
`mlflow.data` API — <https://mlflow.org/docs/latest/api_reference/python_api/mlflow.data.html>.

### System metrics — observability under load (capstone section)

Model metrics answer "is it accurate?"; **system metrics** answer "what did it cost to
train, and is this hardware the bottleneck?" — the resource-observability half of MLOps. The
capstone should add a section that logs host CPU / RAM / disk / network / **GPU** as
time-series metrics during a real, heavy training run, so the reader sees the resource story
next to the accuracy story.

**API:**
- Per run: `mlflow.start_run(log_system_metrics=True)`, or globally
  `mlflow.enable_system_metrics_logging()` (env var `MLFLOW_ENABLE_SYSTEM_METRICS_LOGGING=true`).
- Cadence: `mlflow.set_system_metrics_sampling_interval(seconds)` and
  `mlflow.set_system_metrics_samples_before_logging(n)` (defaults: sample every 10 s, log
  every sample). For a short training run, drop the interval (e.g. 1–2 s) so the charts have
  enough points to be legible.
- Metrics land under the **`system/`** namespace (e.g. `system/cpu_utilization_percentage`,
  `system/system_memory_usage_megabytes`, `system/gpu_0_utilization_percentage`,
  `system/gpu_0_memory_usage_megabytes`) and render as time series in the run's UI.

**Dependencies:** `psutil` (CPU/RAM/disk/net) already ships with MLflow. **GPU metrics need
`pynvml`** — not currently installed; add it with `uv add pynvml`. Without it, MLflow silently
logs everything *except* the `system/gpu_*` series.

**This laptop (verified):** 22 cores, **62 GB RAM**, **NVIDIA RTX 2000 Ada Generation Laptop
GPU**. So the GPU panel is real here — but only if the training actually uses the GPU.

**A big enough workload to move the needle.** California housing (~20 k rows) won't dent 62 GB
of RAM or touch the GPU, so the lifecycle steps (train→register→serve) stay on California
housing for continuity, and the system-metrics section adds a **dedicated "scale" run**:
- **Large dataset:** generate a large synthetic regression set with
  `sklearn.datasets.make_regression` (dial `n_samples`/`n_features` up to a few GB of arrays
  — e.g. ~5–20 M rows × ~50–100 features) so `system/system_memory_usage_*` clearly climbs.
  Note the chosen size and that it's tunable to the reader's RAM.
- **GPU training:** sklearn's `RandomForestRegressor` is **CPU-only** and will never light up
  the GPU. Use **XGBoost on CUDA** (`XGBRegressor(device="cuda", tree_method="hist")`) — already
  a project dependency — so `system/gpu_0_*` shows real utilization. Frame the contrast:
  CPU forest vs GPU boosting, and what each does to the system charts.
- **Teaching point:** tie it back to right-sizing hardware and cost — the reason production
  teams log system metrics at all.

**Sources:** system metrics docs —
<https://mlflow.org/docs/latest/ml/tracking/system-metrics/>; XGBoost GPU support —
<https://xgboost.readthedocs.io/en/stable/gpu/index.html>.

**Gap this proves:** the upstream sklearn guide *narrates* this chain as prose reference
sections, but there is no runnable, single-model capstone. That's the hole.

**Sources:**
- Tutorials & examples index — <https://mlflow.org/docs/latest/ml/tutorials-and-examples/>
- MLflow for Traditional ML — <https://mlflow.org/docs/latest/ml/traditional-ml/>
- sklearn guide (closest end-to-end narrative) — <https://mlflow.org/docs/latest/ml/traditional-ml/sklearn/guide/>
- Autolog overview — <https://mlflow.org/docs/latest/ml/tracking/autolog/>
- `mlflow.sklearn` / `mlflow.xgboost` API — <https://mlflow.org/docs/latest/python_api/mlflow.sklearn.html>, <https://mlflow.org/docs/latest/python_api/mlflow.xgboost.html>
- `examples/multistep_workflow/` (closest official "pipeline").

**Depends on:** `c_`, `f_`, `g_`, `h_` — all now done, so this is unblocked.

---

## Sequencing

```
autolog backfill ──► b_ (one-line alternative)  ┐
                     c_ (max_tuning_runs)        ├─ independent, small commits
                     e_ (xgboost aside)          ┘

f_ (done) ──► g_ registry (done) ──► h_ serving (done) ──► i_capstone (next)
```

The autolog backfill and the capstone are independent — either can come first. Suggested
order: the **`b_` autolog section** (quick, high-leverage), then the **capstone**, then the
**`c_`/`e_`** autolog touch-ups.

**Dependencies to add (via `uv add`, when actually used):**
- `pynvml` — **required for the capstone's GPU system-metrics section** (the NVIDIA RTX 2000
  Ada is present, but `pynvml` is not installed; without it the `system/gpu_*` series are
  silently skipped).
- `shap` — optional, for richer `evaluate()` artifacts in the capstone. The autolog sections
  and `g_`/`h_` need no new deps; `requests` ships with MLflow and `xgboost` is already present.

## Beyond this roadmap (not yet planned)

Candidate future topics once the capstone lands, in rough priority order:
- **MLflow Projects / packaging** (`MLproject`, reproducible `mlflow run`) — the
  `examples/sklearn_elasticnet_wine` / `multistep_workflow` story.
- **Remote/team setup** — backend store on a real DB, artifact store on S3/GCS, the
  client/server split (`examples/remote_store`).
- **Deployment targets deep-dive** — SageMaker / Kubernetes / Modal (mostly platform).
- **GenAI track** — explicitly out of scope for this traditional-ML repo, but `h_`'s "Next
  steps" already points readers there (`mlflow.genai.evaluate`, tracing) as the natural Part 2.
  Note the boundary so readers know where it diverges.
