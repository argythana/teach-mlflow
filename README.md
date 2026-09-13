# Teach MLflow — from beginner to advanced

Tutorials and teaching material for MLflow, aimed at researchers and data scientists who know Python and ML but are new to tracking servers, model serving, and MLOps.

MLflow has evolved rapidly and gained wide adoption. Since version 3 it has grown into a platform for tracking both traditional ML experiments and modern AI / LLM workflows.

Most ML courses, meanwhile, teach algorithms and their metrics as standalone topics and skip the reproducibility, observability, and monitoring that scientific research and production ML systems depend on.

MLflow is not taught at any Computer Science university in Greece, even though it is essential for data scientists. The goal of this repo is to provide beginner-friendly, up-to-date learning resources that help fill that gap.

## The tutorials

Notebooks are grouped by track. Each folder is prefixed `a_`, `b_`, `c_`, … so the intended reading order is obvious from `ls`. Each one stays close to the official MLflow material but adds the prerequisites, terminology, and "why this feature exists" context the upstream docs assume or skip.

**`basics/` — shared foundations** (local server on port `5000`), the starting point for either track:

- `a_setup_mlflow` — what MLflow solves; `mlflow ui` vs `mlflow server`; connecting a notebook to a tracking server.
- `b_tracking_quickstart` — log a model, parameters, and metrics; the three stores (backend / artifact / registry); loading a model back as a `pyfunc`.

**`ml/` — traditional-ML track** (local server on port `5001`):

- `a_model_logging` — logging scikit-learn models well: safe serialization with `skops`, and the one-line `mlflow.sklearn.autolog()`.
- `b_hyperparameter_tuning` — an Optuna sweep with parent/child runs, and a first look at the model registry.
- `c_logging_plots` — log EDA and diagnostic figures across a sweep with `mlflow.log_figure`.
- `d_logging_callbacks` — XGBoost + Optuna callbacks; parent-run metric history vs stdout heartbeats.
- `e_model_evaluation` — `mlflow.models.evaluate()`, custom metrics, and validation gates (CI for models).
- `f_model_registry` — versions, `@champion` / `@challenger` aliases, the promotion lifecycle, and rollback.
- `g_model_serving` — serve a registered model over REST with `mlflow models serve`; the `/invocations` contract, signature enforcement, and the container path.
- `h_dataset_logging` — `mlflow.data` + `log_input` for dataset lineage (raw vs engineered features, digests).
- `i_system_metrics` — `system/*` resource observability (CPU / RAM / GPU) under a heavy training load.
- `j_capstone_end_to_end` — one model through the full lifecycle: feature-engineer → tune → evaluate → gate → register → serve.

That completes the traditional-ML MLOps spine (tracking → evaluation → registry → serving).

**`gen_ai/` — GenAI / LLM track** (local server on port `5001`): tracing, LLM-as-judge evaluation, the prompt registry, serving, and feedback and monitoring — where the MLflow **Traces** tab lights up.

Status: **feature-complete (drafts)**. All nine notebooks are written, in reading order, but not all have been run end to end, so some stored outputs may be missing or out of date. Besides the tracking server, the track needs a local Ollama model and, for five notebooks, a hosted Azure OpenAI deployment — see [GenAI track prerequisites](#genai-track-prerequisites).

- `a_tracing_quickstart` — automatic and manual tracing (`mlflow.openai.autolog()`, `@mlflow.trace`) against a local Ollama model; spans, traces, and the Traces tab.
- `b_tracing_a_multistep_app` — a hand-built RAG pipeline with nested retriever / chain / LLM spans, and how the trace shows which step produced a bad answer.
- `c_genai_evaluation` — `mlflow.genai.evaluate()` with built-in and custom LLM-as-judge scorers, using an Azure OpenAI judge.
- `d_langchain_agent` — a tool-using LangChain agent traced by the one-line `mlflow.langchain.autolog()`.
- `e_prompt_registry` — register, version, and alias prompts, then promote the version the `c_` judge prefers.
- `f_genai_app_serving` — log a GenAI app with models-from-code and serve it over REST on port `5002`; prompt promotions reach the endpoint with no redeploy.
- `g_feedback_and_monitoring` — human and code feedback on traces (`log_feedback`), and LLM-judge monitoring over `search_traces`.
- `h_dspy_optimization` — (advanced) a DSPy optimizer improves a prompt against a metric while `mlflow.dspy.autolog()` records each compile.
- `i_rag_capstone` — the finale: Azure embeddings, a Milvus Lite index, and a LlamaIndex query engine, traced, evaluated, prompt-versioned, and monitored; its serving step points back to `f_`.

See `roadmap/` for the design decisions behind each track and what is planned next.

## Start the MLflow tracking server first

Every notebook assumes a local MLflow tracking server is already running. **Before opening a notebook**, start it in a separate terminal from the `src/` folder, on the port that notebook expects — the `basics/` notebooks use `5000`; the `ml/` and `gen_ai/` tracks use `5001`:

```bash
cd src/
mlflow ui --host 127.0.0.1 --port 5000   # use 5001 for the ml/ and gen_ai/ tracks
```

Leave it running and open the UI at the matching address (e.g. <http://127.0.0.1:5000>). In MLflow 3 this creates a `mlflow.db` (the SQLite backend store) and an `mlartifacts/` directory in the folder you started the server from. Start it from `src/` every time so they stay in one place, next to the notebooks; the notebooks' on-disk examples assume that layout. Both are per-developer runtime state and are gitignored.

If a notebook cell calls `mlflow.set_tracking_uri("http://127.0.0.1:<port>")` while no server is listening on that port, the logging calls will fail.

## Setup

Requires Python **3.14** and [`uv`](https://docs.astral.sh/uv/) for dependency management.

```bash
uv sync          # creates .venv/ and installs locked dependencies
```

`direnv` auto-activates the venv via `.envrc`; otherwise `source .venv/bin/activate`.

## GenAI track prerequisites

The `gen_ai/` notebooks call a language model, so they need more than the tracking server.

**A local Ollama model (free, no API key).** Install [Ollama](https://ollama.com) and pull the default model with `ollama pull qwen3:1.7b` (about a 1.4 GB download). It runs on a GPU when the model fits and falls back to the CPU otherwise, just more slowly. The default is small yet still calls tools reliably, which `d_langchain_agent` needs. [`src/setup/a_ollama_setup.ipynb`](src/setup/a_ollama_setup.ipynb) walks through the setup.

`a_`, `b_`, `d_`, and `f_` call only Ollama (`f_` also expects the prompt that `e_` registers). `c_`, `e_`, and `g_` use Ollama to produce the answers and traces they grade.

**A hosted Azure OpenAI deployment (paid per call).** These notebooks call Azure OpenAI and stop with a `KeyError` if its credentials are missing:

- `c_genai_evaluation` — the LLM-as-judge.
- `e_prompt_registry` — the judge that picks the winning prompt version.
- `g_feedback_and_monitoring` — the monitoring judge.
- `h_dspy_optimization` — the model DSPy optimizes against.
- `i_rag_capstone` — the embeddings, the answering model, and the judge.

Each of the five opens with a short note on what it needs and on its stored outputs, so you can still read them without an Azure deployment.

`a_tracing_quickstart` also has an optional Azure section, and `d_langchain_agent` shows a commented-out Azure swap.

Put the credentials in a `.env` file at the repo root. `.env` is gitignored, so your keys stay out of commits, and the notebooks load it with `python-dotenv`. Replace each angle-bracket placeholder with a value from your own Azure resource:

```bash
# .env at the repo root (gitignored; never commit real values)
AZURE_OPENAI_API_KEY=<your-api-key>
AZURE_OPENAI_BASE_URL=https://<your-resource>.openai.azure.com
AZURE_OPENAI_API_VERSION=2024-10-21
AZURE_OPENAI_LIGHT_MODEL=<your-chat-deployment-name>
AZURE_OPENAI_EMBED_MODEL=<your-embedding-deployment-name>
```

| Variable | Read by | What to put there |
|---|---|---|
| `AZURE_OPENAI_API_KEY` | the five notebooks above | Your resource's API key. Required. |
| `AZURE_OPENAI_BASE_URL` | the five notebooks above | Your resource's endpoint. Required. A trailing `/openai` also works. |
| `AZURE_OPENAI_API_VERSION` | the five notebooks above | The API version. Optional: defaults to `2024-10-21`. |
| `AZURE_OPENAI_LIGHT_MODEL` | the five notebooks above | The name of *your* chat-model deployment; a fast, cheap tier (nano / mini) is enough. Defaults to `gpt-5.4-nano`, which works only if your deployment has that name. |
| `AZURE_OPENAI_EMBED_MODEL` | `i_rag_capstone` | The name of *your* `text-embedding-3-small` deployment. |

## References

- [MLflow documentation](https://mlflow.org/docs/latest/index.html)
- [MLflow GitHub](https://github.com/mlflow/mlflow)

## License

The code in this repository, including the notebooks' code cells, is licensed under the [MIT License](LICENSE). The tutorial prose, in the Markdown files and the notebooks' text cells, is licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE-CC-BY-4.0.txt). If you reuse the prose, credit it with this line and say whether you changed it: "[teach-mlflow](https://github.com/argythana/teach-mlflow) by Thanasis Argyriou, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)."
