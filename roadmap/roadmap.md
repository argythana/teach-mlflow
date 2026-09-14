# Teach-MLflow roadmap (summary)

A living summary of what this teaching repo covers and what's planned. The detailed
per-notebook design history of the traditional-ML track lives in git history; this file
is the scannable overview. The build-out plan for the GenAI track is in
[`plan.md`](./plan.md).

## Repository structure

Notebooks are grouped by track under `src/`, each folder lettered `a_`, `b_`, … for
reading order:

- **`src/basics/`** — track-agnostic foundations both tracks build on.
- **`src/ml/`** — the traditional-ML track (complete).
- **`src/gen_ai/`** — the GenAI / LLM track: feature-complete (drafts); see `plan.md`.

## `basics/` — shared foundations (port 5000)

| #   | Notebook                | Topic                                                                                                                                |
| --- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| a   | `a_setup_mlflow`        | Install, `mlflow ui` vs `server`, tracking URI, start the server, the UI (incl. the Traces-tab orientation note).                    |
| b   | `b_tracking_quickstart` | Experiments, runs, log params/metrics/model, load back as a pyfunc; the three stores. GenAI readers skim the sklearn worked example. |

## `ml/` — traditional-ML track ✅ complete (port 5001)

| #   | Notebook                  | Topic                                                                                       |
| --- | ------------------------- | ------------------------------------------------------------------------------------------- |
| a   | `a_model_logging`         | Safe `skops` serialization + one-line `mlflow.sklearn.autolog()` (split out of `basics/b_`) |
| b   | `b_hyperparameter_tuning` | Optuna sweep, parent/child runs, first registry touch                                       |
| c   | `c_logging_plots`         | `mlflow.log_figure` across a sweep                                                          |
| d   | `d_logging_callbacks`     | XGBoost + Optuna callbacks; parent metric history vs stdout                                 |
| e   | `e_model_evaluation`      | `mlflow.models.evaluate()`, custom metrics, validation gates                                |
| f   | `f_model_registry`        | Versions, `@champion`/`@challenger` aliases, promotion, rollback                            |
| g   | `g_model_serving`         | `mlflow models serve`, `/invocations`, signature enforcement, Docker                        |
| h   | `h_dataset_logging`       | `mlflow.data` + `log_input`, raw vs engineered, digests                                     |
| i   | `i_system_metrics`        | `system/*` observability (CPU/RAM/GPU) under load                                           |
| j   | `j_capstone_end_to_end`   | One model through the full lifecycle on one dataset                                         |

The traditional-ML MLOps spine is built end to end: **track → evaluate & gate → register
& promote → serve**, with dataset lineage and resource observability as standalone
topics and a capstone that threads them together. Spine dataset: California housing
(`fetch_california_housing`, ~20 k rows); synthetic `make_regression` only where scale
is the lesson (`i_system_metrics`). Aliases, not deprecated stage transitions,
throughout.

## `gen_ai/` — GenAI / LLM track ✅ feature-complete (drafts, port 5001 shared with `ml/`)

**LLM backend (decided): fully local-default, hosted optional.** The whole track runs on
a **local Ollama** model (zero cost, no API key — fits the "students with no budget"
audience), with a one-line swap to a hosted model (OpenAI or Azure) shown in each
notebook that benefits. This now includes the parts that used to need a hosted model:

- **LLM-as-judge** (`c_`/`e_`/`g_`/`i_`) uses MLflow's native **`ollama:/gemma3:4b`**
  judge provider, with `temperature=0` (via each scorer's `inference_params`) so scores
  reproduce run-to-run. Eval runs serially (`MLFLOW_GENAI_EVAL_MAX_WORKERS=1`) so a
  single local model isn't overwhelmed by parallel judge calls.
- **DSPy** (`h_`) optimizes against `ollama_chat/gemma3:4b` through LiteLLM (a
  non-reasoning model parses cleanly into DSPy's typed fields).
- **RAG embeddings** (`i_`) use the local **`nomic-embed-text`** model (768-dim) into
  Milvus Lite.

Ollama is a documented *system prerequisite*, like the tracking server — not a pip
dependency. Added Python deps: `openai`, the LangChain v1 stack (`d_`), `dspy` (`h_`),
and the LlamaIndex + Milvus stack incl. `llama-index-embeddings-ollama` /
`llama-index-llms-ollama` (`i_`). `huggingface_hub[cli]` is a dev dep for browsing GGUF
models.

**Default model:** `gemma3:4b` (~3 GB; fits a small GPU, or runs on CPU) — small, fast,
and *non-reasoning*, so it answers directly: no `/no_think` needed, and none of qwen3's
hidden-reasoning-eats-the-token-budget failure mode (which returned empty answers). One
notebook, `d_langchain_agent`, needs tool-calling and uses **`qwen3:1.7b`** instead (1.4
GB; the smallest Qwen3 that still calls tools reliably — thinking left on, since an
agent has to plan), because `gemma3:4b` doesn't support tools. Embedding model for `i_`:
`nomic-embed-text` (274 MB). Reader-facing setup walkthrough:
[`src/setup/a_ollama_setup.ipynb`](../src/setup/a_ollama_setup.ipynb).

**Status:** `a_`–`i_` **built, run live on local Ollama, and contiguous** — the full
GenAI track, ending in `i_rag_capstone` (a realistic Milvus Lite + LlamaIndex RAG that
threads the whole track). `a_` tracing quickstart; `b_` hand-built RAG; `c_`
LLM-as-judge (local `ollama:/` judge, `temperature=0`); `d_` LangChain tool-agent traced
by one-line `mlflow.langchain.autolog()`; `e_` prompt registry (register/version/alias +
promote the version that wins the `c_` judge); `f_` serves a GenAI app over REST
(models-from-code); `g_` closes the loop — human/code feedback (`log_feedback`) +
LLM-judge monitoring over `search_traces`; `h_` DSPy optimization; `i_` the RAG
capstone. Each notebook keeps a hosted-model (Azure/OpenAI) swap as an optional section.

| #   | Notebook                            | Teaches                                                                                                                                                                                                                                                                                                                   | Parallels (ml)            |
| --- | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------- |
| a   | `a_tracing_quickstart` ✅           | The Traces tab lights up: `mlflow.openai.autolog()` against Ollama's OpenAI-compatible endpoint + a manual `@mlflow.trace`.                                                                                                                                                                                               | the basics quickstart     |
| b   | `b_tracing_a_multistep_app` ✅      | Hand-built RAG (no framework): nested `RETRIEVER`/`CHAIN`/`LLM` spans; the failure-diagnosis payoff.                                                                                                                                                                                                                      | —                         |
| c   | `c_genai_evaluation` ✅             | `mlflow.genai.evaluate()` with built-in + custom scorers; judge = local `ollama:/gemma3:4b` (`temperature=0` for reproducible scores); hosted Azure/OpenAI judge shown as an optional swap.                                                                                                                               | `e_model_evaluation`      |
| d   | `d_langchain_agent` ✅              | A tool-using LangChain agent traced by one-line `mlflow.langchain.autolog()` — the framework alternative to `b_`'s manual spans, on a runtime-decided agent loop.                                                                                                                                                         | —                         |
| e   | `e_prompt_registry` ✅              | `register_prompt`, versions + aliases, load by alias, and promote the version that wins the `c_` LLM-as-judge comparison.                                                                                                                                                                                                 | `f_model_registry`        |
| f   | `f_genai_app_serving` ✅            | Log a GenAI app via models-from-code, `mlflow models serve` it on 5002, curl `/invocations`; the served app loads `qa-answer@production` per request, so prompt promotion ships with no redeploy.                                                                                                                         | `g_model_serving`         |
| g   | `g_feedback_and_monitoring` ✅      | Human + code feedback on traces (`log_feedback`); LLM-judge monitoring over `search_traces` (OSS). Flags the Databricks-managed boundary.                                                                                                                                                                                 | —                         |
| h   | `h_dspy_optimization` (advanced) ✅ | A DSPy optimizer (`BootstrapFewShot`) auto-improves a prompt against a metric; `mlflow.dspy.autolog()` records every compile + saves the optimized program. Local Ollama LM via LiteLLM (`ollama_chat/gemma3:4b`, non-reasoning so it parses cleanly); Azure optional. The prompt analog of `ml/b_hyperparameter_tuning`. | `b_hyperparameter_tuning` |
| i   | `i_rag_capstone` ✅                 | Realistic RAG finale: local **nomic-embed-text** embeddings → **Milvus Lite** index (`dim=768`) → LlamaIndex query engine (traced) → retrieval + answer judge eval → prompt registry → feedback/monitor → serve (← `f_`). Fully local; Azure swap shown commented. Threads the whole track.                               | `j_capstone_end_to_end`   |

**Advanced notebooks (built):**

- **DSPy prompt optimization — built as `h_dspy_optimization`.** Chose **DSPy over
  AdalFlow** (a PyTorch-like textual-gradient optimizer): DSPy has first-class MLflow
  integration (`mlflow.dspy.autolog()` autologs the optimization); AdalFlow is elegant
  for an ML audience and Ollama-native, but its MLflow story isn't native, so it loses
  for an *MLflow* tutorial. AdalFlow is noted in `h_` as the alternative paradigm.
- **LlamaIndex / Milvus RAG — built as `i_rag_capstone`** (the GenAI finale). Resolved
  the "full notebook vs `b_` appendix" question by making it the realistic capstone:
  local `nomic-embed-text` embeddings + **Milvus Lite** + LlamaIndex,
  traced/evaluated/governed/served end to end, with the `c_` retrieval scorers finally
  grading a real retriever.

**Editorial stance** (per the `mlflow-tutorial-improve` skill): lead with the *problem*
(you can't put a number on "is this answer good?" → LLM-as-judge; you can't see inside a
chain → tracing), define GenAI jargon once (span, trace, scorer, judge, prompt version),
and cross-link the `ml/` analog rather than re-teaching shared MLflow concepts.

## Sequencing

```text
basics/ (a_setup → b_tracking_quickstart)
   ├─► ml/      a_ … j_   ✅ complete
   └─► gen_ai/  a_ → b_ → c_ → d_ → e_ (prompts) → f_ (serving) → g_ (feedback)   ✅
                → h_ (DSPy) → i_ (realistic RAG capstone)   ✅  (a_–i_ built and run on local Ollama)
```

## Beyond this roadmap (not yet planned)

- **MLflow Projects / packaging** (`MLproject`, reproducible `mlflow run`).
- **Remote/team setup** — backend store on a real DB, artifact store on S3/GCS.
- **Deployment targets deep-dive** — SageMaker / Kubernetes / Modal.
- **A `databricks/` track (managed-only features).** `g_` is where the repo first meets
  the OSS ceiling: the **Review App** + **labeling sessions** (human-in-the-loop UI),
  **scheduled scorers** (`ScorerScheduleConfig`, auto-monitoring on live traffic), Unity
  Catalog governance, and managed serving endpoints all need a **Databricks workspace**.
  The repo so far is fully OSS (Databricks features flagged as managed *alternatives*,
  never required). If we cover them, they'd form a separate, clearly-prerequisited
  `databricks/` folder — its bar (a workspace) sits above this repo's "students with no
  budget" audience, so it stays optional.
