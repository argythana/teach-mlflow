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
| i | `i_dataset_logging` | `mlflow.data` + `log_input`, raw vs engineered, digests | advanced | ✅ done |
| j | `j_system_metrics` | `system/*` observability under load (RAM/GPU) | advanced | ✅ done |
| k | `k_capstone_end_to_end` | One model through the full lifecycle | advanced | ✅ done |

The traditional-ML MLOps spine is now built end to end: **track** (`b`–`e`) → **evaluate &
gate** (`f`) → **register & promote** (`g`) → **serve** (`h`). What remains is the
**autologging backfill** into existing notebooks (see "Autolog: backfill into existing
notebooks"), two **standalone feature notebooks** — `i_dataset_logging` and
`j_system_metrics` — and finally the **capstone** (`k`) that runs *one* model through the
whole spine on *one* dataset, cross-linking `i_`/`j_` instead of re-teaching them.

**Why the capstone was split (decided June 2026).** The earlier plan bundled the lifecycle
chain **+** dataset logging **+** system-metrics-under-load into a single `i_capstone`. That's
three notebooks' worth and breaks the repo's "keep notebooks short and single-topic" rule, so
dataset logging and system metrics each became their own focused notebook, and the capstone
shrank to just the narrative lifecycle thread.

## TODO / backlog (at a glance)

The actionable list. Details live in the sections below.

- [x] **`e_` XGBoost autolog aside** — **done.** Markdown aside before `e_`'s "Next steps": `mlflow.xgboost.autolog()` gives the *within-training* (per-boosting-round) curve + feature-importance plot for free, but **can't** produce the study-level `best_so_far` convergence across Optuna trials (different axis) — complementary to the manual callbacks, not redundant. Completes the autolog backfill (`b_`/`c_`/`e_` all done).
- [x] **`i_dataset_logging`** — **done** (built + executed live, June 2026). 27-cell standalone notebook on California housing: raw + engineered two-`log_input` pattern, the autolog-vs-manual contrast (verified: manual → named `local`-source datasets; autolog → generic `dataset`/`code` source), the digest fingerprint gotcha, `source.load()` reload, `evaluate(data=)` tag-vs-`log_input` nuance, `MetaDataset`. Writes re-loadable CSVs to gitignored `_dataset_demo/`.
- [x] **`j_system_metrics`** — **done** (built + executed live, June 2026). 21-cell standalone notebook: `log_system_metrics=True`, 1 s sampling cadence, the 13-metric `system/*` namespace, and a CPU-vs-GPU XGBoost contrast on a 5 M×50 synthetic set (verified: GPU run ~12 s/99% GPU util vs CPU run ~52 s/95% CPU util). Surfaces the **`nvidia-ml-py` vs deprecated `pynvml`** drift and the **host-wide (not per-process)** caveat.
- [x] **`k_capstone_end_to_end`** — **done** (built + executed live, June 2026). 21-cell lifecycle chain on California housing: feature-engineer + dataset logging (`i_`) → tune 3 RF candidates as child runs with system metrics on (`c_`/`j_`) → `evaluate` each (`f_`) → gate winner vs a `DummyRegressor` baseline (`f_`) → register + `@champion`/`@challenger` (`g_`) → load champion → **live `mlflow models serve` on 5002 + curl `/invocations`** (`h_`, used not re-taught) with REST==in-process verified. Includes the **Traces-tab orientation note**. **This completes the roadmap.**
- [x] **`uv add nvidia-ml-py`** — **done.** Needed for `j_`'s `system/gpu_*` metrics. NB: the roadmap originally said `uv add pynvml`, but `pynvml` is now a **deprecated** shim that warns on import — the correct current package is **`nvidia-ml-py`** (it provides the same `pynvml` module). `uv add shap` is still optional (richer `evaluate()` artifacts).
- [ ] **Traces orientation note** — short in-scope cell explaining what the (always-empty-for-traditional-ML) **Traces** tab is and where it lights up. Lands in `k_`'s wrap-up; one-line forward pointer optional from `b_`'s UI tour. See "The Traces tab" below.
- [x] **Optional — enhance `c_`'s autolog aside:** **done.** Added a markdown note after the GridSearch comparison: **no native `mlflow.optuna.autolog()`** (Optuna isn't a training-library flavor), and the Optuna-side `optuna_integration.MLflowCallback` is **deprecated** (`@deprecated_class("4.9.0", "6.0.0")`) — so the manual nested-run pattern stays the durable one.
- [x] **Optional — `h_` backfill:** **done.** Added a "Step 1.5" `mlflow.models.predict()` pre-serve smoke test (validate the logged model loads + predicts, by default in a dependency-isolated env), executed live; regenerated `h_` against a fresh self-contained champion so all cells agree (smoke test == REST == in-process).

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
- **One small real spine dataset; synthetic only for scale (decided June 2026).** California
  housing (`fetch_california_housing`, one-line load, ~20 k rows) is the continuity dataset
  across `b_`–`h_` and the capstone. It's already tiny, so no "load a small sample" step is
  needed — and you *cannot sample it up* to stress hardware. The hardware-stress lesson lives
  only in `j_system_metrics`, which uses **synthetic `make_regression`** (large + zero
  download) plus **GPU XGBoost** for that one purpose. We considered swapping in one large
  *real* dataset everywhere, but that trades away one-line beginner loading and would retrofit
  six already-shipped notebooks for continuity that `d_`–`h_` largely already have — not worth
  it. (`b_` staying on iris is fine; an optional, low-priority continuity nicety, not a rewrite.)
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

**Deltas vs plan:**
- The **`mlflow.models.predict()` pre-serve smoke test** (validate a model in an isolated env
  before standing up a server) — **now added** as "Step 1.5" (June 2026).
- No **MLServer-deprecation** note — but `h_` never teaches `--enable-mlserver`, so this is moot.

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
| **`e_logging_callbacks`** ✅ **done** | "Aside: `mlflow.xgboost.autolog()` gives the *within-training* curve for free" | Markdown aside before "Next steps": `mlflow.xgboost.autolog()` captures **per-boosting-round metrics + feature-importance plots** for free (the Step-7 plot, essentially), but operates on *one fit at a time* so it **can't** build the parent-run study-level convergence — that's a different axis (Optuna trial #, not boosting round). Recipe: autolog on the children, keep `mlflow_progress_callback` on the parent. Cross-links `b_`/`c_`; carries the `ubj`-format caveat. *(Markdown-only; no execution needed.)* |

**Recommended sequencing:** **all three autolog backfills (`b_`/`c_`/`e_`) are now done.**
Each landed in its own small commit.

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

## i_dataset_logging (✅ done — advanced)

Standalone notebook (split out of the old capstone, June 2026). The motivating moment is real
**feature engineering**: once the columns the model trains on differ from the raw data, "which
data + which features produced this model?" is no longer answerable from the run's params and
metrics alone. `mlflow.data` + `mlflow.log_input` record that lineage. This notebook does a
small feature-engineering example on California housing so it stands alone; the capstone (`k_`)
then *cross-links* here rather than re-teaching it.

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

**Resolved (June 2026):** this is **its own notebook** (`i_dataset_logging`), not a capstone
section — it has clean standalone value and the capstone was over-stuffed. The capstone reuses
it by cross-link at the feature-engineering step.

**Sources:** dataset tracking guide — <https://mlflow.org/docs/latest/ml/dataset/>;
`mlflow.data` API — <https://mlflow.org/docs/latest/api_reference/python_api/mlflow.data.html>.

---

## j_system_metrics (✅ done — advanced)

Standalone notebook (split out of the old capstone, June 2026). Model metrics answer "is it
accurate?"; **system metrics** answer "what did it cost to train, and is this hardware the
bottleneck?" — the resource-observability half of MLOps. This notebook logs host CPU / RAM /
disk / network / **GPU** as time-series metrics during a real, heavy training run, so the
reader sees the resource story next to the accuracy story.

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

**Dependencies:** `psutil` (CPU/RAM/disk/net) already ships with MLflow. **GPU metrics need the
`pynvml` module — installed via `uv add nvidia-ml-py`** (NVIDIA's official bindings; the older
standalone `pynvml` package is deprecated and warns on import). Without it, MLflow silently logs
everything *except* the `system/gpu_*` series. *(Added June 2026.)*

**This laptop (verified):** 22 cores, **62 GB RAM**, **NVIDIA RTX 2000 Ada Generation Laptop
GPU**. So the GPU panel is real here — but only if the training actually uses the GPU.

**A big enough workload to move the needle.** California housing (~20 k rows, the repo's spine
dataset) won't dent 62 GB of RAM or touch the GPU, and you can't sample it *up*. So this
notebook uses a **dedicated synthetic "scale" run** purely to make the charts move — the only
place in the repo that departs from the California-housing spine, and deliberately so:

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

---

## k_capstone_end_to_end (✅ done — advanced)

**Purpose.** One realistic, continuous workflow on **one** dataset/model (California housing +
RandomForest/XGBoost) that closes the loop the official docs leave fragmented. This is the
notebook that makes the whole repo cohere — and now that dataset logging (`i_`) and system
metrics (`j_`) are their own notebooks, the capstone is *just the narrative lifecycle thread*.

**The chain (each step reuses an earlier notebook's concept, doesn't re-teach it):**

1. **Feature-engineer** the raw data and **log both the raw and engineered datasets** —
   cross-link `i_dataset_logging` for the mechanics; here just *do* it.
2. Tune a few candidate models with child runs (`c_`) — optionally via `autolog()`,
   cross-linking rather than re-teaching it.
3. `mlflow.models.evaluate()` to pick the best by held-out RMSE/R² (`f_`).
4. Gate the winner with `validate_evaluation_results` against a baseline (`f_`).
5. `register_model(...)` the model that passed → assign `@champion`; keep runner-up as
   `@challenger` (`g_`).
6. Load `models:/...@champion` and sanity-check (`g_`).
7. `mlflow models serve` + curl a real prediction (`h_`).
8. **Optionally** flip on `log_system_metrics=True` for the heavy tuning step — cross-link
   `j_system_metrics`; don't re-teach the namespace.

**Design constraints:**
- Keep it a *capstone*, not a re-teach: link back to `c_`/`f_`/`g_`/`h_`/`i_`/`j_` for the
  "why," and spend the prose on the **decisions** that connect the steps ("select the best,
  gate it, promote *that one*, serve it"). The official material never makes those decisions
  explicit because evaluation is siloed from registry/serving.
- Acknowledge the official toy framing once (wine-quality ElasticNet / iris) and explain why
  we use California housing + RandomForest/XGBoost instead (continuity + a richer target).
- This is the first notebook that exercises **both** extra processes at once (tracking on
  5001, serving on 5002) — spell out the terminal setup, as `h_` does.

### The Traces tab — orientation note (in-scope; not a tracing tutorial)

A reader on MLflow 3 sees a **Traces** tab next to Runs/Models that is **always empty** for
traditional-ML work, and reasonably asks "what is this?" Answer it in one short cell in the
capstone wrap-up (with an optional one-line forward pointer from `b_`'s first UI tour):

- **What it is:** MLflow Tracing records OpenTelemetry-style **spans** (inputs/outputs/latency
  per step) — built for **GenAI/LLM apps and agents** (LangChain, OpenAI, LlamaIndex, …),
  where you want to see *inside* a chain/RAG/agent call.
- **Why it's empty here:** sklearn/XGBoost runs produce no spans; nothing in this repo emits
  traces. The tab populating requires GenAI instrumentation (`@mlflow.trace` / a GenAI
  autolog flavor).
- **Where it goes next:** that's the GenAI track — out of scope for this traditional-ML repo
  (see "Beyond this roadmap"). The note exists for **MLflow-3 UI literacy**, not to teach
  tracing. A full tracing tutorial would be a deliberate scope expansion (`j_`-style GenAI
  notebook, new LLM dep) — deferred.
- **Sources:** tracing overview — <https://mlflow.org/docs/latest/genai/tracing/>.

**Gap this proves:** the upstream sklearn guide *narrates* this chain as prose reference
sections, but there is no runnable, single-model capstone. That's the hole.

**Sources:**

- Tutorials & examples index — <https://mlflow.org/docs/latest/ml/tutorials-and-examples/>
- MLflow for Traditional ML — <https://mlflow.org/docs/latest/ml/traditional-ml/>
- sklearn guide (closest end-to-end narrative) — <https://mlflow.org/docs/latest/ml/traditional-ml/sklearn/guide/>
- Autolog overview — <https://mlflow.org/docs/latest/ml/tracking/autolog/>
- `mlflow.sklearn` / `mlflow.xgboost` API — <https://mlflow.org/docs/latest/python_api/mlflow.sklearn.html>, <https://mlflow.org/docs/latest/python_api/mlflow.xgboost.html>
- `examples/multistep_workflow/` (closest official "pipeline").

**Depends on:** `c_`, `f_`, `g_`, `h_` (all done) plus `i_dataset_logging` and
`j_system_metrics` — build those two first, then the capstone cross-links them.

---

## Sequencing

```text
autolog backfill ──► b_ (one-line alternative)  ┐
   (all done)        c_ (max_tuning_runs)        ├─ independent, small commits
                     e_ (xgboost aside)          ┘

f_ (done) ──► g_ registry (done) ──► h_ serving (done) ──┐
                                                         ├─► k_capstone (last)
i_dataset_logging  ─┐                                    │
j_system_metrics   ─┴─ standalone feature notebooks  ───┘
```

**The roadmap is complete.** Autolog backfill (`b_`/`c_`/`e_`), `i_dataset_logging`,
`j_system_metrics`, and the `k_capstone_end_to_end` finale are all built and executed live.
Remaining items are the *optional* touch-ups below (e.g. `h_`'s `mlflow.models.predict()` smoke
test) and the future topics in "Beyond this roadmap."

**Dependencies:**

- `nvidia-ml-py` — **added** (June 2026); provides the `pynvml` module `j_system_metrics` uses
  for its GPU series. The standalone `pynvml` package is deprecated — use `nvidia-ml-py`.
- `shap` — optional, for richer `evaluate()` artifacts in the capstone. The autolog sections,
  `i_`, `j_`, and `g_`/`h_` need no further deps; `requests` ships with MLflow and `xgboost` is
  already present.

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
