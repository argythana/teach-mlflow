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

## `gen_ai/` — GenAI / LLM track 🔧 in progress

**LLM backend (decided):** teach against a **local Ollama** model (zero cost, no API key —
fits the "students with no budget" audience) and show the one-line swap to the **OpenAI API**.
Ollama is a documented *system prerequisite*, like the tracking server — not a pip dependency.
The `openai` client (which talks to both Ollama and OpenAI) is added to the project, and
`huggingface_hub[cli]` is a dev dep for browsing GGUF models on HF (Ollama can run any GGUF via
`ollama run hf.co/<repo>:<quant>`).

**Default model:** `qwen3:8b` (5.2 GB, fits an 8 GB GPU; host has ~64 GB RAM). It's a reasoning
model — notebooks append `/no_think` for clean, fast traces and turn thinking on where it's the
point. Lighter alt: `gemma3:4b`.

**Status:** `a_`–`d_` **drafted and contiguous**. `a_tracing_quickstart` ✅ verified (Ollama +
Azure). `b_` hand-built RAG; `c_` LLM-as-judge (Azure judge via MLflow's native `azure:/`
provider — no `litellm`; judges read `AZURE_API_KEY`/`AZURE_API_BASE`/`AZURE_API_VERSION`,
mapped from the repo's `AZURE_OPENAI_*`); `d_` LangChain tool-agent traced by one-line
`mlflow.langchain.autolog()` (stack verified live on Ollama). `b_`–`d_` need full runs to
capture outputs. `e_`–`g_` planned.

| # | Notebook | Teaches | Parallels (ml) |
|---|----------|---------|----------------|
| a | `a_tracing_quickstart` ✅ | The Traces tab lights up: `mlflow.openai.autolog()` against Ollama's OpenAI-compatible endpoint + a manual `@mlflow.trace`. | the basics quickstart |
| b | `b_tracing_a_multistep_app` ✅ | Hand-built RAG (no framework): nested `RETRIEVER`/`CHAIN`/`LLM` spans; the failure-diagnosis payoff. | — |
| c | `c_genai_evaluation` ✅ | `mlflow.genai.evaluate()` with built-in + custom scorers; judge = `azure:/<deployment>`. | `e_model_evaluation` |
| d | `d_langchain_agent` ✅ | A tool-using LangChain agent traced by one-line `mlflow.langchain.autolog()` — the framework alternative to `b_`'s manual spans, on a runtime-decided agent loop. | — |
| e | `e_prompt_registry` | `register_prompt`, versions + aliases, compare in the UI, evaluate prompt versions. | `f_model_registry` |
| f | `f_genai_app_serving` (advanced) | Log a GenAI app/agent (models-from-code) and serve it. | `g_model_serving` |
| g | `g_feedback_and_monitoring` (stretch) | Human feedback / assessments on traces; production-monitoring scorers. | — |

**Advanced / under discussion:**

- **DSPy + MLflow optimization** (planned advanced, companion to `e_prompt_registry`): a DSPy
  program MLflow *optimizes* (`mlflow.genai.optimize_prompts`) and traces via
  `mlflow.dspy.autolog()` — the unique MLflow×framework pairing. Conceptually heavier, so it
  sits beside the prompt-registry notebook, not as the intro framework notebook (`d_` fills
  that with LangChain).
- **LlamaIndex / Milvus RAG** *(for discussion — decide before building)*: a "production RAG"
  notebook that swaps `b_`'s toy lexical retriever for a LlamaIndex `VectorStoreIndex` backed by
  a **Milvus** vector store, traced by `mlflow.llama_index.autolog()`, with the retrieval
  scorers (`RetrievalRelevance`/`RetrievalGroundedness`) from `c_`. **Pro:** real embeddings + a
  real vector DB, end to end. **Con:** heavy deps (`llama-index`, a running Milvus, an embedding
  model) and conceptual overlap with `b_`/`d_`. Open question: worth a full notebook, or a short
  appendix to `b_`?

**Editorial stance** (per the `mlflow-tutorial-improve` skill): lead with the *problem* (you
can't put a number on "is this answer good?" → LLM-as-judge; you can't see inside a chain →
tracing), define GenAI jargon once (span, trace, scorer, judge, prompt version), and
cross-link the `ml/` analog rather than re-teaching shared MLflow concepts.

## Sequencing

```text
basics/ (a_setup → b_tracking_quickstart)
   ├─► ml/      a_ … j_   ✅ complete
   └─► gen_ai/  a_ ✅ → b_ → c_ → d_ (langchain agent) → e_ (prompts) → f_ (serving) → g_ (feedback)   🔧
                b_ (multistep) and f_ (feedback) are enrichment, not blockers
```

## Beyond this roadmap (not yet planned)

- **MLflow Projects / packaging** (`MLproject`, reproducible `mlflow run`).
- **Remote/team setup** — backend store on a real DB, artifact store on S3/GCS.
- **Deployment targets deep-dive** — SageMaker / Kubernetes / Modal.
