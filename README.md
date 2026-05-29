# Groww-Style MF Facts-Only FAQ Prototype

A Streamlit + LangChain RAG assistant styled as a Groww extension prototype. It answers factual questions about selected HDFC Mutual Fund schemes using only approved public sources. This prototype is not supported by Groww.

## What It Does

- Answers facts about selected HDFC Mutual Fund schemes.
- Uses only official HDFC Mutual Fund, AMFI, and SEBI sources.
- Includes one source URL in each tested/guarded answer.
- Refuses investment advice, portfolio recommendations, and return projections.
- Blocks PAN, Aadhaar, account numbers, OTPs, emails, and phone numbers.
- Persists embeddings locally in `./chroma_db` for faster later startup.
- Provides a professional Groww-inspired HTML/React UI (`frontend/`) connected to the RAG API.
- Optional legacy Streamlit UI (`app.py`) with light and dark mode.

## Requirements

- Python 3.10+
- Groq API key in `.env`
- Internet access on first run for source loading and embedding model download

## Environment

Create or update `.env` in this folder:

```bash
GROQ_LIP4=your_groq_key_here
```

The backend also supports `GROQ_API_KEY` if you prefer that name:

```bash
GROQ_API_KEY=your_groq_key_here
```

## Install

From the project folder, use a virtual environment so `pip` and `streamlit` share the same Python:

```bash
cd /Users/rushilv698/NextLeap/LIP4
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If you already use Python 3.13 from python.org, you can install there instead:

```bash
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 -m pip install -r requirements.txt
```

## Run The Professional Frontend (recommended)

Serves the design handoff UI and RAG API on one port:

```bash
cd /Users/rushilv698/NextLeap/LIP4
source .venv/bin/activate   # if using a venv
uvicorn api:app --reload --port 8000
```

Open **http://localhost:8000** — landing → login → chat, with answers from `rag_assistant.py` via `POST /api/ask`.

Frontend files live in `frontend/` (from `faq-assistant-working-prototype/project/FAQ Assistant.html`).

## Run Streamlit (optional)

Start the Streamlit server (with the same environment you used for install):

```bash
cd /Users/rushilv698/NextLeap/LIP4
source .venv/bin/activate   # if using a venv
streamlit run app.py
```

Or with the python.org 3.13 interpreter:

```bash
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 -m streamlit run app.py
```

Then open the local URL Streamlit prints, usually:

```text
http://localhost:8501
```

If port `8501` is already busy, run on another port:

```bash
streamlit run app.py --server.port 8502
```

## First Run Behavior

On first launch, the app will:

1. Load approved web sources from `source_list.py`.
2. Split documents into chunks.
3. Download/use `all-MiniLM-L6-v2` embeddings.
4. Build and persist the Chroma index in `./chroma_db`.
5. Start answering questions through Groq-hosted `llama-3.3-70b-versatile`.

Later launches reuse `./chroma_db` unless the source registry changes.

## Backend Smoke Test

Run this to confirm the backend works without opening the UI:

```bash
cd /Users/rushilv698/NextLeap/LIP4
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 - <<'PY'
from rag_assistant import answer_question, build_qa_chain

qa = build_qa_chain()
question = "What is the expense ratio of HDFC Top 100 Fund direct plan?"
print(answer_question(qa, question))
PY
```

Expected answer shape:

```text
The TER/expense ratio for HDFC Top 100 Fund Direct Plan is 1.06%. Source: https://www.hdfcfund.com/product-solutions/overview/hdfc-top-100-fund/direct. Last updated from sources: YYYY-MM-DD.
```

## Frontend

| Path | Role |
|------|------|
| `frontend/index.html` | Professional UI shell (React + Babel, from design handoff) |
| `frontend/*.jsx` | Landing, login, chat screens |
| `api.py` | FastAPI: `POST /api/ask` + static file server |
| `app.py` | Optional Streamlit UI (older prototype) |

- UI assets: `frontend/assets/groww-logo.png`
- Not affiliated with or supported by Groww.

### User flow (HTML UI)

1. **Landing** — Hero, trust row, popular HDFC example questions.
2. **Login** — Mobile/Google prototype login (no real auth).
3. **Chat** — Questions call `POST /api/ask`; answers use the same RAG chain as smoke tests, with source links parsed into the UI.

## Architecture

- `source_list.py`: single approved source registry.
- `rag_assistant.py`:
  - loads/splits documents from approved URLs (`WebBaseLoader`, `PyPDFLoader`),
  - embeds with `all-MiniLM-L6-v2`,
  - persists vectors in `./chroma_db` (ChromaDB),
  - rebuilds Chroma automatically when the approved source registry changes,
  - blocks PII, investment advice, and return projection questions before retrieval,
  - builds a Groq RetrievalQA chain using `llama-3.3-70b-versatile`.
- `api.py`: FastAPI server exposing `/api/ask` and serving `frontend/`.
- `app.py`: Optional Streamlit UI for question input and answer display.

## Supported Scope

- HDFC Top 100 Fund / HDFC Large Cap Fund page
- HDFC Flexi Cap Fund
- HDFC ELSS Tax Saver Fund
- HDFC Balanced Advantage Fund
- Investor service questions, including capital gains statement guidance
- AMFI/SEBI educational and regulatory material

## Usage

- Ask factual questions about expense ratios, exit loads, SIP minimums, lock-ins, riskometers, benchmarks, and statements.
- The assistant returns concise answers with source attribution.
- The approved source registry contains 33 official HDFC Mutual Fund, AMFI, and SEBI URLs (verified May 2026).

## Validation Note

- Query validated: `What is the expense ratio of HDFC Top 100 Fund direct plan?`
- Verified against official HDFC page payload on May 29, 2026.
- Current published value found on source page: `terDirecct: 1.06` (direct plan TER/expense ratio).
- Source: https://www.hdfcfund.com/product-solutions/overview/hdfc-top-100-fund/direct

## Troubleshooting

- If the first run is slow, wait for source ingestion and embedding setup to finish.
- If Chroma appears stale after changing sources, delete `./chroma_db` and rerun the app.
- If `streamlit` is not found, confirm dependencies were installed in the same Python environment used to run the app.
- If you see `ModuleNotFoundError: langchain_core`, reinstall with `pip install -r requirements.txt` in the active venv (Homebrew `python3` and python.org 3.13 are different installs).
- If Groq calls fail, confirm `.env` contains `GROQ_LIP4` or `GROQ_API_KEY`.
- If port `8501` is in use, run `streamlit run app.py --server.port 8502`.

## Limitations

- Uses only content available in the approved source registry.
- Refuses investment advice and return projections.
- Does not accept PAN, Aadhaar, account numbers, OTPs, emails, or phone numbers.
- If source pages change structure or become unavailable, retrieval quality may degrade.
