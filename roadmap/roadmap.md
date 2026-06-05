# Teach-MLflow roadmap (summary)

A living summary of what this teaching repo covers and what's planned. The detailed
per-notebook design history of the traditional-ML track lives in git history; this file is
the scannable overview. The build-out plan for the GenAI track is in [`plan.md`](./plan.md).

## Repository structure

Notebooks are grouped by track under `src/`, each folder lettered `a_`, `b_`, … for reading
order:

- **`src/basics/`** — track-agnostic foundations both tracks build on.
- **`src/ml/`** — the traditional-ML track (complete).
- **`src/gen_ai/`** — the GenAI / LLM track (planned — see `plan.md`).

## `basics/` — shared foundations (port 5000)

| # | Notebook | Topic |
|---|----------|-------|
| a | `a_setup_mlflow` | Install, `mlflow ui` vs `server`, tracking URI, start the server, the UI (incl. the Traces-tab orientation note). |
| b | `b_tracking_quickstart` | Experiments, runs, log params/metrics/model, load back as a pyfunc; the three stores. GenAI readers skim the sklearn worked example. |

## `ml/` — traditional-ML track ✅ complete (port 5001)

| # | Notebook | Topic |
|---|----------|-------|
| a | `a_model_logging` | Safe `skops` serialization + one-line `mlflow.sklearn.autolog()` (split out of `basics/b_`) |
| b | `b_hyperparameter_tuning` | Optuna sweep, parent/child runs, first registry touch |
| c | `c_logging_plots` | `mlflow.log_figure` across a sweep |
| d | `d_logging_callbacks` | XGBoost + Optuna callbacks; parent metric history vs stdout |
| e | `e_model_evaluation` | `mlflow.models.evaluate()`, custom metrics, validation gates |
| f | `f_model_registry` | Versions, `@champion`/`@challenger` aliases, promotion, rollback |
| g | `g_model_serving` | `mlflow models serve`, `/invocations`, signature enforcement, Docker |
| h | `h_dataset_logging` | `mlflow.data` + `log_input`, raw vs engineered, digests |
| i | `i_system_metrics` | `system/*` observability (CPU/RAM/GPU) under load |
| j | `j_capstone_end_to_end` | One model through the full lifecycle on one dataset |

The traditional-ML MLOps spine is built end to end: **track → evaluate & gate → register &
promote → serve**, with dataset lineage and resource observability as standalone topics and a
capstone that threads them together. Spine dataset: California housing (`fetch_california_housing`,
~20 k rows); synthetic `make_regression` only where scale is the lesson (`i_system_metrics`).
Aliases, not deprecated stage transitions, throughout.

## `gen_ai/` — GenAI / LLM track 🔜 planned

**LLM backend (decided):** teach against a **local Ollama** model (zero cost, no API key —
fits the "students with no budget" audience) and show the one-line swap to the **OpenAI API**.
Ollama is a documented *system prerequisite*, like the tracking server — not a pip dependency.

| # | Notebook | Teaches | Parallels (ml) |
|---|----------|---------|----------------|
| a | `a_tracing_quickstart` | The Traces tab lights up: `mlflow.openai.autolog()` against Ollama's OpenAI-compatible endpoint + a manual `@mlflow.trace`. Spans = inputs/outputs/latency. | the basics quickstart |
| b | `b_tracing_a_multistep_app` | A small RAG / tool-using chain: nested spans, framework autolog (LangChain or LlamaIndex). *Why* tracing matters. | — |
| c | `c_genai_evaluation` | `mlflow.genai.evaluate()` with LLM-as-judge scorers (correctness, relevance, groundedness, guidelines) + a custom scorer; eval datasets. | `e_model_evaluation` |
| d | `d_prompt_registry` | `register_prompt`, prompt versions + aliases, compare in the UI, load by alias, evaluate prompt versions. | `f_model_registry` |
| e | `e_genai_app_serving` (advanced) | Log a GenAI app/agent (models-from-code / `ResponsesAgent`) and serve it. | `g_model_serving` |
| f | `f_feedback_and_monitoring` (stretch) | Human feedback / assessments on traces; production-monitoring scorers on live traffic. | — |

**Editorial stance** (per the `mlflow-tutorial-improve` skill): lead with the *problem* (you
can't put a number on "is this answer good?" → LLM-as-judge; you can't see inside a chain →
tracing), define GenAI jargon once (span, trace, scorer, judge, prompt version), and
cross-link the `ml/` analog rather than re-teaching shared MLflow concepts.

## Sequencing

```text
basics/ (a_setup → b_tracking_quickstart)
   ├─► ml/      a_ … j_   ✅ complete
   └─► gen_ai/  a_ (tracing) → c_ (eval) → d_ (prompts) → e_ (serving)   🔜
                b_ (multistep) and f_ (feedback) are enrichment, not blockers
```

## Beyond this roadmap (not yet planned)

- **MLflow Projects / packaging** (`MLproject`, reproducible `mlflow run`).
- **Remote/team setup** — backend store on a real DB, artifact store on S3/GCS.
- **Deployment targets deep-dive** — SageMaker / Kubernetes / Modal.
