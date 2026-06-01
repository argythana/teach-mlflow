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
See "Autolog: now homeless" below.

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
| **`b_tracking_quickstart`** *(primary)* | "The one-line alternative: `mlflow.autolog()`" | After the manual `log_param`/`log_metric`/`log_model` walkthrough, show `mlflow.sklearn.autolog()` capturing the same params + metrics + model + **signature** automatically. The defaults table with the **`log_input_examples=False` gotcha**, universal `mlflow.autolog()` vs flavor-specific precedence, and the **control-vs-convenience / surprise-artifacts trade-off**. This is the natural home because `b_` is where manual tracking is introduced — readers meet the shortcut right after learning the long way. Fits the repo's `## MISSING FROM THE OFFICIAL TUTORIAL` pattern. |
| **`c_hyperparameter_tuning`** | "Autolog and search: `max_tuning_runs`" | `c_` does GridSearchCV/child runs by hand; autolog's `max_tuning_runs` (default 5; `None` = all) produces the *parent best-run + child runs* automatically. One short contrast cell: "you wired this up manually — autolog does it in one line, here's what differs." |
| **`e_logging_callbacks`** | one-paragraph aside | `e_` already does XGBoost callbacks; note that `mlflow.xgboost.autolog()` captures **per-iteration metrics + feature-importance plots** for free, and when you'd still reach for explicit callbacks. Cross-link, don't re-teach. |

**Recommended sequencing:** do the **`b_`** section first (it's the conceptual anchor and the
most reused), then the **`c_`** section, then the **`e_`** aside. Each is independent and can
land in its own small commit.

**Version-drift to surface in the `b_` section:** MLflow 3 logs models as first-class
**LoggedModel** entities; `log_datasets=True` and `log_models=True` are defaults;
`log_input_examples=False` is *not*. Sources: autolog overview
<https://mlflow.org/docs/latest/ml/tracking/autolog/>, `mlflow.sklearn`/`mlflow.xgboost` API
refs.

---

## i_capstone_end_to_end (next — advanced)

**Purpose.** One realistic, continuous workflow on **one** dataset/model that closes the loop
the official docs leave fragmented. This is the notebook that makes the whole repo cohere.

**The chain (each step reuses an earlier notebook's concept, doesn't re-teach it):**
1. Tune a few candidate models with child runs (`c_`) — optionally via `autolog()` once the
   `c_` autolog section exists, cross-linking rather than re-teaching it.
2. `mlflow.models.evaluate()` to pick the best by held-out RMSE/R² (`f_`).
3. Gate the winner with `validate_evaluation_results` against a baseline (`f_`).
4. `register_model(...)` the model that passed → assign `@champion`; keep runner-up as
   `@challenger` (`g_`).
5. Load `models:/...@champion` and sanity-check (`g_`).
6. `mlflow models serve` + curl a real prediction (`h_`).

**Design constraints:**
- Keep it a *capstone*, not a re-teach: link back to `c_`/`f_`/`g_`/`h_` for the "why," and
  spend the prose on the **decisions** that connect the steps ("select the best, gate it,
  promote *that one*, serve it"). The official material never makes those decisions explicit
  because evaluation is siloed from registry/serving.
- Acknowledge the official toy framing once (wine-quality ElasticNet / iris) and explain why
  we use California housing + RandomForest/XGBoost instead (continuity + a richer target).
- This is the first notebook that exercises **both** extra processes at once (tracking on
  5001, serving on 5002) — spell out the terminal setup, as `h_` does.

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
```
