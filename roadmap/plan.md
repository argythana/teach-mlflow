# Plan: GenAI tutorial track + shared `basics/`

The forward-looking build plan. For the at-a-glance status of both tracks see
[`roadmap.md`](./roadmap.md).

## Context

The repo regrouped notebooks into `src/ml/` (traditional-ML, complete) and an empty
`src/gen_ai/` placeholder. We are building out the **GenAI track** without re-teaching
the foundations both tracks share. Two foundations are track-agnostic — `a_setup_mlflow`
(infrastructure) and `b_tracking_quickstart` (experiments, runs, the three stores) — so
they now live in `src/basics/`.

**Decisions taken:**

1. **LLM backend: fully local-default, hosted optional.** Every GenAI notebook runs on a
   local Ollama model (zero cost, no API key — fits the "students with no budget"
   audience), with a one-line swap to a hosted model (OpenAI/Azure) shown where it
   helps. The default is **`gemma3:4b`** — small, fast, non-reasoning — for generation
   *and* the judges (MLflow's native `ollama:/gemma3:4b`, `temperature=0`); DSPy's LM is
   `ollama_chat/gemma3:4b`; RAG embeddings use `nomic-embed-text` (768-dim). The one
   exception is `d_langchain_agent`, which needs tool-calling and uses `qwen3:1.7b`
   (gemma3:4b doesn't support tools). Ollama is a documented *system prerequisite*, like
   the tracking server — not a pip dependency.
1. **`basics/` holds `a_setup` + the whole `b_tracking_quickstart`.** `b_`'s second half
   stays sklearn-flavored; a skim note tells GenAI readers the tracking concepts above
   are what matter and the model-logging mechanics belong to the `ml/` track.

## Done (this restructure)

- Created `src/basics/`; moved `a_setup_mlflow` + `b_tracking_quickstart` there.

- Split the scikit-learn–only material out of `basics/b_` into a new
  `ml/a_model_logging` (safe `skops` serialization + `mlflow.sklearn.autolog()`);
  `basics/b_` keeps the shared spine (experiments, params/metrics,
  `log_model`→pyfunc→predict, store layout) with a brief skops pointer. Renumbered the
  rest of `src/ml/` → `b_`–`j_`.

- Swept every cross-reference + the docs (`README.md`, `CLAUDE.md`, the skill); updated
  `a_setup`'s Traces-tab note (GenAI is now an in-repo track, not "out of scope") and
  its "What's next" branch (basics → `ml/` / `gen_ai/`); updated the `b_` skim note.

- Created this `roadmap/` folder.

- Ran `ml/a_model_logging` (port 5001) and re-ran `basics/b_` so outputs reflect the
  split. The `ml/` track is now complete end to end.

## GenAI notebooks (`src/gen_ai/`) — built

Built one at a time against a local Ollama model, in this sequence:

| #   | Notebook                               | Teaches                                                                                                                                                                                                                                                                                                     | Parallels (ml)        |
| --- | -------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------- |
| a   | `a_tracing_quickstart` ✅ drafted      | The Traces tab lights up. Ollama prereq + `mlflow.openai.autolog()` against Ollama's OpenAI-compatible endpoint + a manual `@mlflow.trace`. Spans = inputs/outputs/latency.                                                                                                                                 | the basics quickstart |
| b   | `b_tracing_a_multistep_app` ✅ drafted | Hand-built RAG (no framework): a traced `RETRIEVER` span + `CHAIN` root + autologged `LLM` span; the failure-diagnosis payoff. Notes framework autolog as the one-line alternative.                                                                                                                         | —                     |
| c   | `c_genai_evaluation` ✅ drafted        | `mlflow.genai.evaluate()` with built-in judges (RelevanceToQuery, Guidelines, Correctness) + a custom `@scorer` + a `predict_fn` app. **Judge = local `ollama:/gemma3:4b`** via MLflow's native ollama provider (`temperature=0`, serial eval); a hosted Azure/OpenAI judge is an optional swap at the end. | `e_model_evaluation`  |
| d   | `d_langchain_agent` ✅ drafted         | Tool-using LangChain agent (`langchain.agents.create_agent`, langchain v1) on Ollama, traced by one-line `mlflow.langchain.autolog()` — the framework alternative to `b_`'s manual spans. Runs on `qwen3:1.7b`, the one notebook that needs a tool-calling model.                                           | —                     |
| e   | `e_prompt_registry` ✅ drafted         | `register_prompt` (auto-versions), `{{var}}` templates, `set_prompt_alias`, `load_prompt("prompts:/name@alias")`; compares v1 vs v2 by running each through Ollama and scoring with the `c_` local judge, then promotes the winner.                                                                         | `f_model_registry`    |
| f   | `f_genai_app_serving` ✅ drafted       | models-from-code pyfunc (loads `qa-answer@production` per request) → `mlflow models serve -p 5002 --env-manager local` (needs `MLFLOW_TRACKING_URI` for the registry) → curl `/invocations`. Notes the `d_` agent serves the same way via `mlflow.langchain.log_model`.                                     | `g_model_serving`     |
| g   | `g_feedback_and_monitoring` ✅ drafted | `log_feedback` (HUMAN + CODE source) on traces (needs `flush_trace_async_logging`), read back via `get_trace`; monitoring = `search_traces` + `mlflow.genai.evaluate(data=traces, scorers=[judge])`. Flags Review App / labeling / scheduled scorers as Databricks-managed.                                 | —                     |

**Advanced notebooks (built):**

- **DSPy** — **built as `h_dspy_optimization`** (`BootstrapFewShot` +
  `mlflow.dspy.autolog()`, local Ollama LM through LiteLLM: `ollama_chat/gemma3:4b`).
  Chose DSPy over AdalFlow for native MLflow integration; AdalFlow noted in `h_` as the
  alternative.
- **LlamaIndex / Milvus RAG — built as `i_rag_capstone`** (the GenAI finale): local
  `nomic-embed-text` embeddings + Milvus Lite + LlamaIndex,
  traced/evaluated/governed/served, with a milvus-lite 3.0 `output_fields` search
  workaround baked into the notebook.

**Editorial stance** (per the `mlflow-tutorial-improve` skill): lead with the *problem*,
define GenAI jargon once (span, trace, scorer, judge, prompt version), cross-link the
`ml/` analog instead of re-teaching shared MLflow concepts.

**Dependencies:** **added** — `openai`, `python-dotenv`, the LangChain v1 stack
(`langchain`/`langchain-openai`/`langgraph`) for `d_`, `dspy` (brings `litellm`) for
`h_`, and for `i_` the LlamaIndex packages (`llama-index-core`,
`llama-index-vector-stores-milvus`, `llama-index-embeddings-ollama`,
`llama-index-llms-ollama`, and for the optional hosted swap
`llama-index-embeddings-azure-openai`, `llama-index-llms-azure-openai`) plus `pymilvus`,
which bundles Milvus Lite. **Ollama is a documented system prerequisite**, not a Python
dependency.

## Build order

`a_` → … → `i_` are built and contiguous — the GenAI track is **feature-complete
(drafts)**: every notebook is written and runs end to end on local Ollama.
`i_rag_capstone` is the realistic finale. Remaining: a possible future `databricks/`
track for managed-only features (Review App, labeling, scheduled scorers) — see
roadmap.md.
