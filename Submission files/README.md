# Groww-Style Multi-AMC MF Facts-Only FAQ Assistant

A RAG-powered FAQ assistant styled as a Groww prototype. Answers factual questions about mutual fund schemes from HDFC, Kotak, SBI, and Nippon India using only approved official sources — with source attribution in every answer.

> **Prototype only. Not affiliated with or supported by Groww.**

---

## What It Does

- Answers factual questions about MF schemes across four AMCs: **HDFC, Kotak, SBI, Nippon India**.
- Sources data only from official AMC, AMFI, and SEBI pages (58 approved URLs).
- Returns every answer with a specific source page link (not just the AMC homepage).
- Refuses investment advice, portfolio recommendations, and return projections.
- Blocks PAN, Aadhaar, account numbers, OTPs, emails, and phone numbers.
- Persists embeddings locally in `./chroma_db` — fast restarts after first build.
- Groww-inspired React UI served directly by the FastAPI backend on a single port.

---

## Architecture

```
Browser  (http://localhost:8002)
  └── frontend/index.html          ← React shell (Babel in-browser, no build step)
        ├── screens.jsx            ← Landing + Login screens
        ├── chat.jsx               ← Chat UI, AMC selector, topic chips
        ├── icons.jsx              ← SVG icons
        └── app.jsx                ← Client-side router
              │
              │  POST /api/ask     ← ask a question
              │  GET  /api/amcs    ← list supported AMCs and schemes
              │  GET  /api/health  ← health check
              ▼
        api.py  (FastAPI — serves API + static frontend)
              ▼
        rag_assistant.py
              ├── source_list.py          58 approved URLs
              ├── WebBaseLoader / PyPDFLoader
              ├── ChromaDB  ./chroma_db   local vector store
              ├── all-MiniLM-L6-v2        HuggingFace embeddings
              └── llama-3.3-70b-versatile via Groq API
```

---

## Supported Schemes

| AMC | Schemes |
|-----|---------|
| **HDFC** | Top 100 Fund, Flexi Cap Fund, ELSS Tax Saver, Balanced Advantage Fund |
| **Kotak** | Flexi Cap Fund, ELSS Tax Saver Fund, Bluechip Fund, Balanced Advantage Fund |
| **SBI** | Bluechip Fund, Long Term Equity Fund, Flexicap Fund, Balanced Advantage Fund |
| **Nippon India** | Large Cap Fund, Tax Saver ELSS, Flexi Cap Fund, Balanced Advantage Fund |

---

## Requirements

- Python 3.10+
- Groq API key in `.env`
- Internet access on first run (source loading + embedding model download)

---

## Environment Setup

Create `.env` in the project folder:

```bash
GROQ_API_KEY=your_groq_key_here
```

Also accepted: `GROQ_LIP4` as the key name.

---

## Install

```bash
cd /Users/rushilv698/NextLeap/LIP4
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Or with the system Python 3.13:

```bash
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 -m pip install -r requirements.txt
```

---

## Run

```bash
cd /Users/rushilv698/NextLeap/LIP4
python3 -m uvicorn api:app --reload --port 8002
```

Then open **http://localhost:8002** — landing → login → chat.

> Ports 8000 and 8001 may be occupied by other projects on this machine; use 8002 or higher if needed.

---

## First-Run Behaviour

On first launch the server will:

1. Load all 58 approved URLs (`source_list.py`).
2. Split each page into chunks and prepend `[Source: url]` to each chunk.
3. Download `all-MiniLM-L6-v2` embeddings (cached after first download).
4. Build and persist a ChromaDB index in `./chroma_db`.
5. Start answering questions via Groq `llama-3.3-70b-versatile`.

Subsequent launches reuse `./chroma_db` automatically. If `source_list.py` changes, the index rebuilds on the next request.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/ask` | Ask a question; returns `type`, `body`, `source`, `last_updated` |
| `GET` | `/api/amcs` | List supported AMCs and their scheme names |
| `GET` | `/api/health` | Health check with source count |
| `GET` | `/` | Serves the React frontend |

### Example — ask a question

```bash
curl -X POST http://localhost:8002/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the exit load of HDFC Flexi Cap Fund?"}'
```

Response:
```json
{
  "type": "answer",
  "body": "The exit load of HDFC Flexi Cap Fund is 1.00% if Units are redeemed / switched-out within 1 year from the date of allotment...",
  "source": {
    "label": "HDFC Mutual Fund — Official source",
    "url": "https://www.hdfcfund.com/explore/mutual-funds/hdfc-flexi-cap-fund/direct"
  },
  "last_updated": "2026-05-30"
}
```

---

## Approved Sources (58 URLs)

| Category | Count |
|----------|-------|
| HDFC Mutual Fund pages | 25 |
| Kotak Mutual Fund pages | 6 |
| SBI Mutual Fund pages | 6 |
| Nippon India MF pages (`mf.nipponindiaim.com`) | 6 |
| AMFI investor education pages | 8 |
| SEBI investor education pages | 7 |

Full list: [`source_list.py`](source_list.py) / [`source_list.csv`](source_list.csv)

---

## Project Structure

```
LIP4/
├── api.py                  FastAPI backend + static file server
├── rag_assistant.py        RAG core (load, chunk, embed, retrieve, answer)
├── source_list.py          Approved URL registry (58 sources)
├── source_list.csv         Same registry as CSV (with AMC column)
├── requirements.txt        Python dependencies (no Streamlit)
├── sample_qa.md            Representative Q&A examples
├── .env                    Groq API key (gitignored)
├── chroma_db/              Persisted ChromaDB vector store
└── frontend/
    ├── index.html          App shell + all CSS
    ├── app.jsx             Client router
    ├── screens.jsx         Landing + Login screens
    ├── chat.jsx            Chat screen, AMC selector, chips
    ├── icons.jsx           SVG icon components
    └── assets/
        └── groww-logo.png
```

---

## Smoke Test

Confirm the backend answers correctly without opening the UI:

```bash
curl -s -X POST http://localhost:8002/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the lock-in period for HDFC ELSS Tax Saver?"}' \
  | python3 -m json.tool
```

Expected:
```json
{
  "type": "answer",
  "body": "HDFC ELSS Tax Saver has a lock-in period of three years.",
  "source": {
    "label": "HDFC Mutual Fund — Official source",
    "url": "https://www.hdfcfund.com/product-solutions/overview/hdfc-elss-tax-saver/direct"
  },
  "last_updated": "2026-05-30"
}
```

---

## User Flow

```
Landing Page  →  Login (prototype, no real auth)  →  Chat
                                                        ├── Select AMC pill (All / HDFC / Kotak / SBI / Nippon)
                                                        ├── Click topic chip (Expense Ratio / Exit Load / …)
                                                        ├── Pick example question or type your own
                                                        └── Receive answer + source citation card
```

---

## Limitations

- Uses only content available in the 58 approved sources.
- AMC scheme pages that render entirely with JavaScript may return limited data (SPA pages are scraped as static HTML).
- Refuses investment advice, return projections, and PII.
- Source page content changes are picked up on the next `chroma_db` rebuild.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Slow first startup | Wait for source ingestion and embedding build (~2–3 min for 58 sources) |
| Stale answers after adding sources | Delete `./chroma_db` and restart — it rebuilds automatically |
| `ModuleNotFoundError: langchain_core` | Run `pip install -r requirements.txt` in the same Python env used to start the server |
| Groq calls fail | Check `.env` contains `GROQ_API_KEY` or `GROQ_LIP4` |
| Port already in use | Change `--port 8002` to any free port |
