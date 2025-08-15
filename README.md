
diff --git a/Project Mental Health/README.md b/Project Mental Health/README.md
--- a/Project Mental Health/README.md
+++ b/Project Mental Health/README.md
@@ -0,0 +1,100 @@
+# Project Mental Health
+
+A Streamlit application that helps users chat with an AI mental health assistant, generate structured daily summaries, and track progress over time with charts.
+
+## Features
+- Chat with an AI mental health assistant powered by LlamaIndex and OpenAI
+- Generate a structured daily summary (score, total conditions considered, narrative content)
+- Persist results per user to `data/user_storage/scores.json`
+- Visualize progress for the last 7 days
+- Simple authentication (login, register, guest)
+
+## Project structure
+```
+Project Mental Health/
+├─ Home.py                     # Streamlit entry page (navigation)
+├─ pages/
+│  ├─ chat.py                  # Chat interface with the AI assistant
+│  └─ user.py                  # Tracking dashboard (chart + history)
+├─ src/
+│  ├─ conversation_engine.py   # Agent setup, chat flow, summary generation & saving
+│  ├─ ingest_pipeline.py       # Ingestion pipeline for DSM-5 reference content
+│  ├─ prompts.py               # System and extraction prompts
+│  ├─ authentication.py        # Login/register/guest logic
+│  ├─ sidebar.py               # Common sidebar UI
+│  ├─ global_settings.py       # Paths (cache, storage, scores file)
+│  └─ index_builder.py         # Helper to build indices (if needed)
+└─ data/
+   ├─ images/                  # UI images
+   ├─ cache/                   # Conversation + pipeline caches
+   ├─ index_storage/           # LlamaIndex persisted index
+   └─ user_storage/
+      └─ scores.json           # Saved tracking records (JSON list)
+```
+
+## Prerequisites
+- Python 3.10 or 3.11 recommended
+- An OpenAI API key
+- A virtual environment (conda or venv)
+
+## Installation
+```bash
+# Create and activate a virtual environment (example with conda)
+conda create -n mental_health python=3.11 -y
+conda activate mental_health
+
+# Upgrade tooling
+pip install -U pip setuptools wheel
+
+# Install compatible dependencies
+pip install "llama-index==0.10.67" "llama-index-core==0.10.67" \
+  "llama-index-llms-openai==0.1.20" "llama-index-embeddings-openai==0.1.11" \
+  "openai[aiohttp]==1.43.0" "httpx==0.27.2" "aiohttp==3.9.5" \
+  streamlit plotly pandas python-docx
+```
+
+## Configuration
+Set your OpenAI API key via environment variable (do not hardcode it):
+```bash
+export OPENAI_API_KEY="sk-..."
+```
+The app reads and writes files under `data/`. Ensure the following folders exist (they are included in this repo):
+- `data/index_storage/`
+- `data/user_storage/`
+- `data/cache/`
+- `data/images/`
+
+## Building/refreshing the index (optional)
+If you need to (re)build the index for DSM-5 content, verify `src/global_settings.py` paths, then run your ingestion/build process. For example:
+```bash
+python -c "from src.ingest_pipeline import ingest_documents; ingest_documents()"
+```
+This will create/update artifacts in `data/index_storage/` and the ingestion cache in `data/cache/`.
+
+## Running the app
+From the project root (folder containing `Home.py`):
+```bash
+streamlit run "Home.py"
+```
+Navigate to the Streamlit UI, log in (or continue as Guest), and:
+- Use the Chat page to converse with the assistant and click “📝 Generate Mental Health Summary”.
+- Use the Tracking page to see your last 7 days’ scores and query details by date.
+
+## How saving works
+- The chat agent does not save automatically during summary generation; the UI requests a structured JSON from the model, parses it, and saves via `save_score`.
+- Records are stored in `data/user_storage/scores.json` as a JSON list.
+- Basic deduplication is applied (same user, same score and content in the last few entries).
+
+## Troubleshooting
+- If you see missing module errors for LlamaIndex components, make sure the versions above are installed together.
+- If the chart does not appear on the Tracking page:
+  - Ensure you have at least one saved record (generate a summary via Chat).
+  - Check that `Score` values are among: Bad, Average, Quite good, Good.
+  - Ensure `data/user_storage/scores.json` is valid JSON (the app can also read JSON-lines from past runs).
+- If you previously hardcoded `openai.api_key`, remove it and use the environment variable instead.
+
+## Security note
+Do not commit API keys. Use environment variables or Streamlit Secrets for deployment.
+
+## License
+This project is for educational/demo purposes. Add your preferred license here.
