# Overview
## 1, What it is: 

- A Streamlit app where users chat with an AI mental health assistant, get a structured daily summary, and track progress over time.
## 2, Key features:

- AI chat: Context-aware assistant (via LlamaIndex + OpenAI).

- One-click summary: Generates score, total_guess, and a concise content report.


- Progress tracking: Last 7 days chart and per-day details.

- Auth: Login, register, or continue as guest.

## 3, Tech stack:

- Frontend: Streamlit + Plotly.

- AI/Indexing: LlamaIndex (core, OpenAI LLM, embeddings), OpenAI SDK.

- Storage: JSON files under data/ (chat history, index, scores).

- Data & files:

+ Scores: data/user_storage/scores.json (JSON array of records).

+ Index: data/index_storage/ (persisted LlamaIndex).

+ Cache: data/cache/ (pipeline/chat history).

+ Images: data/images/.

## 4, How it works:

- Chat conversation builds context.

- “📝 Generate Mental Health Summary” asks the LLM for a JSON-only response.

- The app parses and normalizes fields, then saves via a robust save_score function with deduplication.

- The Tracking page maps scores to numeric values and renders a 7-day chart.

- Run (high level):

Use Python 3.10/3.11, set OPENAI_API_KEY, install compatible LlamaIndex + OpenAI + Streamlit deps.

Start the app:

streamlit run "Home.py"
