# Teach-MLflow roadmap (summary)

A living summary of what this teaching repo covers and what's planned. The detailed
per-notebook design history of the traditional-ML track lives in git history; this file is
the scannable overview. The build-out plan for the GenAI track is in [`plan.md`](./plan.md).

## Repository structure

Notebooks are grouped by track under `src/`, each folder lettered `a_`, `b_`, … for reading
order:

- **`src/basics/`** — track-agnostic foundations both tracks build on.
- **`src/ml/`** — the traditional-ML track (complete).
- **`src/gen_ai/`** — the GenAI / LLM track (in progress — see `plan.md`).

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

## `gen_ai/` — GenAI / LLM track ✅ feature-complete (drafts)

**LLM backend (decided):** teach against a **local Ollama** model (zero cost, no API key —
fits the "students with no budget" audience) and show the one-line swap to the **OpenAI API**.
Ollama is a documented *system prerequisite*, like the tracking server — not a pip dependency.
The `openai` client (which talks to both Ollama and OpenAI) is added to the project, and
`huggingface_hub[cli]` is a dev dep for browsing GGUF models on HF (Ollama can run any GGUF via
`ollama run hf.co/<repo>:<quant>`).

**Default model:** `qwen3:8b` (5.2 GB, fits an 8 GB GPU; host has ~64 GB RAM). It's a reasoning
model — notebooks append `/no_think` for clean, fast traces and turn thinking on where it's the
point. Lighter alt: `gemma3:4b`.

**Status:** `a_`–`i_` **drafted and contiguous** — the full GenAI track, ending in `i_rag_capstone` (a realistic Milvus + LlamaIndex RAG that threads the whole track). All need live runs to capture outputs. `a_tracing_quickstart` ✅ verified (Ollama +
Azure). `b_` hand-built RAG; `c_` LLM-as-judge (Azure judge via MLflow's native `azure:/`
provider — no `litellm`; judges read `AZURE_API_KEY`/`AZURE_API_BASE`/`AZURE_API_VERSION`,
mapped from the repo's `AZURE_OPENAI_*`); `d_` LangChain tool-agent traced by one-line
`mlflow.langchain.autolog()` (stack verified live on Ollama). `e_` is the prompt registry (register/version/alias + promote the winning version with the
`c_` judge). `f_` serves a GenAI app over REST (models-from-code; verified live); `g_` closes the loop — human/code feedback on traces (`log_feedback`) + LLM-judge monitoring over `search_traces` (verified live). `b_`–`g_` need full runs to capture outputs.

| # | Notebook | Teaches | Parallels (ml) |
|---|----------|---------|----------------|
| a | `a_tracing_quickstart` ✅ | The Traces tab lights up: `mlflow.openai.autolog()` against Ollama's OpenAI-compatible endpoint + a manual `@mlflow.trace`. | the basics quickstart |
| b | `b_tracing_a_multistep_app` ✅ | Hand-built RAG (no framework): nested `RETRIEVER`/`CHAIN`/`LLM` spans; the failure-diagnosis payoff. | — |
| c | `c_genai_evaluation` ✅ | `mlflow.genai.evaluate()` with built-in + custom scorers; judge = `azure:/<deployment>`. | `e_model_evaluation` |
| d | `d_langchain_agent` ✅ | A tool-using LangChain agent traced by one-line `mlflow.langchain.autolog()` — the framework alternative to `b_`'s manual spans, on a runtime-decided agent loop. | — |
| e | `e_prompt_registry` ✅ | `register_prompt`, versions + aliases, load by alias, and promote the version that wins the `c_` LLM-as-judge comparison. | `f_model_registry` |
| f | `f_genai_app_serving` ✅ | Log a GenAI app via models-from-code, `mlflow models serve` it on 5002, curl `/invocations`; the served app loads `qa-answer@production` per request, so prompt promotion ships with no redeploy. | `g_model_serving` |
| g | `g_feedback_and_monitoring` ✅ | Human + code feedback on traces (`log_feedback`); LLM-judge monitoring over `search_traces` (OSS). Flags the Databricks-managed boundary. | — |
| h | `h_dspy_optimization` (advanced) ✅ | A DSPy optimizer (`BootstrapFewShot`) auto-improves a prompt against a metric; `mlflow.dspy.autolog()` records every compile + saves the optimized program. Azure LM. The prompt analog of `ml/b_hyperparameter_tuning`. | `b_hyperparameter_tuning` |
| i | `i_rag_capstone` ✅ | Realistic RAG finale: Azure embeddings → **Milvus Lite** index → LlamaIndex query engine (traced) → retrieval + answer judge eval → prompt registry → feedback/monitor → serve (← `f_`). Threads the whole track. | `j_capstone_end_to_end` |

**Advanced / under discussion:**

- **DSPy prompt optimization — built as `h_dspy_optimization`.** Chose **DSPy over AdalFlow**
  (a PyTorch-like textual-gradient optimizer): DSPy has first-class MLflow integration
  (`mlflow.dspy.autolog()` autologs the optimization); AdalFlow is elegant for an ML audience
  and Ollama-native, but its MLflow story isn't native, so it loses for an *MLflow* tutorial.
  AdalFlow is noted in `h_` as the alternative paradigm.
- **LlamaIndex / Milvus RAG — built as `i_rag_capstone`** (the GenAI finale). Resolved the
  "full notebook vs `b_` appendix" question by making it the realistic capstone: real Azure
  embeddings + **Milvus Lite** + LlamaIndex, traced/evaluated/governed/served end to end, with
  the `c_` retrieval scorers finally grading a real retriever.

**Editorial stance** (per the `mlflow-tutorial-improve` skill): lead with the *problem* (you
can't put a number on "is this answer good?" → LLM-as-judge; you can't see inside a chain →
tracing), define GenAI jargon once (span, trace, scorer, judge, prompt version), and
cross-link the `ml/` analog rather than re-teaching shared MLflow concepts.

## Sequencing

```text
basics/ (a_setup → b_tracking_quickstart)
   ├─► ml/      a_ … j_   ✅ complete
   └─► gen_ai/  a_ ✅ → b_ → c_ → d_ → e_ (prompts) → f_ (serving) → g_ (feedback)   🔧
                a_–i_ built (g_ = spine end; h_ = DSPy; i_ = realistic RAG capstone)
```

## Beyond this roadmap (not yet planned)

- **MLflow Projects / packaging** (`MLproject`, reproducible `mlflow run`).
- **Remote/team setup** — backend store on a real DB, artifact store on S3/GCS.
- **Deployment targets deep-dive** — SageMaker / Kubernetes / Modal.
- **A `databricks/` track (managed-only features).** `g_` is where the repo first meets the OSS
  ceiling: the **Review App** + **labeling sessions** (human-in-the-loop UI), **scheduled scorers**
  (`ScorerScheduleConfig`, auto-monitoring on live traffic), Unity Catalog governance, and managed
  serving endpoints all need a **Databricks workspace**. The repo so far is fully OSS (Databricks
  features flagged as managed *alternatives*, never required). If we cover them, they'd form a
  separate, clearly-prerequisited `databricks/` folder — its bar (a workspace) sits above this
  repo's "students with no budget" audience, so it stays optional.
