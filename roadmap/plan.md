# Plan: GenAI tutorial track + shared `basics/`

The forward-looking build plan. For the at-a-glance status of both tracks see
[`roadmap.md`](./roadmap.md).

## Context

The repo regrouped notebooks into `src/ml/` (traditional-ML, complete) and an empty
`src/gen_ai/` placeholder. We are building out the **GenAI track** without re-teaching the
foundations both tracks share. Two foundations are track-agnostic — `a_setup_mlflow`
(infrastructure) and `b_tracking_quickstart` (experiments, runs, the three stores) — so they
now live in `src/basics/`.

**Decisions taken:**
1. **LLM backend: Ollama-default, OpenAI noted.** GenAI notebooks teach against a local
   Ollama model (zero cost, no API key — fits the "students with no budget" audience), and
   show the one-line swap to the OpenAI API. Ollama is a documented *system prerequisite*,
   like the tracking server — not a pip dependency.
2. **`basics/` holds `a_setup` + the whole `b_tracking_quickstart`.** `b_`'s second half
   stays sklearn-flavored; a skim note tells GenAI readers the tracking concepts above are
   what matter and the model-logging mechanics belong to the `ml/` track.

## Done (this restructure)

- Created `src/basics/`; moved `a_setup_mlflow` + `b_tracking_quickstart` there.
- Split the scikit-learn–only material out of `basics/b_` into a new `ml/a_model_logging`
  (safe `skops` serialization + `mlflow.sklearn.autolog()`); `basics/b_` keeps the shared
  spine (experiments, params/metrics, `log_model`→pyfunc→predict, store layout) with a brief
  skops pointer. Renumbered the rest of `src/ml/` → `b_`–`j_`.
- Swept every cross-reference + the docs (`README.md`, `CLAUDE.md`, the skill); updated
  `a_setup`'s Traces-tab note (GenAI is now an in-repo track, not "out of scope") and its
  "What's next" branch (basics → `ml/` / `gen_ai/`); updated the `b_` skim note.
- Created this `roadmap/` folder.

- Ran `ml/a_model_logging` (port 5001) and re-ran `basics/b_` so outputs reflect the split.
  The `ml/` track is now complete end to end.

## To build — GenAI notebooks (`src/gen_ai/`)

Build one at a time, executed live against a local Ollama model. Sequence:

| # | Notebook | Teaches | Parallels (ml) |
|---|----------|---------|----------------|
| a | `a_tracing_quickstart` ✅ drafted | The Traces tab lights up. Ollama prereq + `mlflow.openai.autolog()` against Ollama's OpenAI-compatible endpoint + a manual `@mlflow.trace`. Spans = inputs/outputs/latency. **Authored, no outputs yet — needs a live run.** | the basics quickstart |
| b | `b_tracing_a_multistep_app` | A small RAG / tool-using chain: nested spans, framework autolog (LangChain or LlamaIndex). *Why* tracing matters — see inside a chain. | — |
| c | `c_genai_evaluation` ✅ drafted | `mlflow.genai.evaluate()` with built-in judges (RelevanceToQuery, Guidelines, Correctness) + a custom `@scorer` + a `predict_fn` app. **Judge = `azure:/<deployment>`** via MLflow's native azure provider (map `AZURE_OPENAI_*` → `AZURE_API_KEY`/`AZURE_API_BASE`/`AZURE_API_VERSION`; no litellm). Smoke-tested live; needs a full run. | `e_model_evaluation` |
| d | `d_prompt_registry` | `register_prompt`, prompt versions + aliases, compare in the UI, load by alias, evaluate prompt versions. | `f_model_registry` |
| e | `e_genai_app_serving` (advanced) | Log a GenAI app/agent (models-from-code / `ResponsesAgent`), serve it, the deployment story. | `g_model_serving` |
| f | `f_feedback_and_monitoring` (stretch) | Human feedback / assessments on traces; production-monitoring scorers on live traffic. | — |

**Editorial stance** (per the `mlflow-tutorial-improve` skill): lead with the *problem*,
define GenAI jargon once (span, trace, scorer, judge, prompt version), cross-link the `ml/`
analog instead of re-teaching shared MLflow concepts.

**Dependencies:** the `openai` client (used against Ollama too) is **added** (`uv add openai`).
Still to add as their notebooks land: optionally `langchain` / `llama-index` for the
multistep notebook. **Ollama is a documented system prerequisite**, not
a Python dependency — a first cell should explain installing it and pulling a small model.

## Build order
`a_tracing_quickstart` first (it's the entry point and where the Traces tab finally fills),
then `c_` → `d_` → `e_`. `b_` (multistep) and `f_` (feedback) are enrichment, not blockers.
