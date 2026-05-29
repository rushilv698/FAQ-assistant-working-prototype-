"""FastAPI server: RAG backend + static Groww FAQ frontend."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from rag_assistant import REFRESH_DATE, answer_question, build_qa_chain
from source_list import SOURCE_LIST

load_dotenv()

FRONTEND_DIR = Path(__file__).parent / "frontend"
_qa_chain = None

URL_PATTERN = re.compile(r"https?://[^\s<>\"']+")
DATE_PATTERN = re.compile(r"Last updated from sources:\s*([\d-]+)", re.IGNORECASE)

REFUSAL_MARKERS = (
    "cannot offer investment advice",
    "cannot offer investment advice or future return projections",
    "cannot accept or process",
    "only provide factual information from approved sources",
)

ERROR_MARKERS = (
    "couldn't find that information in the approved sources",
    "could not find this in the approved",
)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


class SourceOut(BaseModel):
    label: str
    url: str


class AskResponse(BaseModel):
    type: str
    heading: str | None = None
    body: str
    source: SourceOut | None = None
    last_updated: str


def get_qa_chain():
    global _qa_chain
    if _qa_chain is None:
        _qa_chain = build_qa_chain()
    return _qa_chain


def _source_label(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if "hdfcfund.com" in host:
        return "HDFC Mutual Fund — Official source"
    if "kotakmf.com" in host:
        return "Kotak Mutual Fund — Official source"
    if "sbimf.com" in host:
        return "SBI Mutual Fund — Official source"
    if "nipponindiaim.com" in host or "nipponindiamf.com" in host:
        return "Nippon India Mutual Fund — Official source"
    if "amfiindia.com" in host:
        return "AMFI — Investor education"
    if "sebi.gov.in" in host:
        return "SEBI — Investor education"
    return host or "Official source"


def _strip_trailing_punctuation(url: str) -> str:
    return url.rstrip(".,);]")


def parse_answer_text(raw: str) -> AskResponse:
    text = raw.strip()
    lowered = text.lower()

    if any(marker in lowered for marker in ERROR_MARKERS):
        msg_type = "error"
    elif any(marker in lowered for marker in REFUSAL_MARKERS):
        msg_type = "refusal"
    else:
        msg_type = "answer"

    urls = [_strip_trailing_punctuation(u) for u in URL_PATTERN.findall(text)]
    source_url = urls[0] if urls else None

    date_match = DATE_PATTERN.search(text)
    last_updated = date_match.group(1) if date_match else REFRESH_DATE

    source = None
    if source_url:
        source = SourceOut(label=_source_label(source_url), url=source_url)

    body = text
    if msg_type in ("answer", "error") and source_url:
        # Remove the full sentence fragment that contains the source URL (e.g. "For more info, visit <url>")
        body = re.sub(r'[^.]*' + re.escape(source_url) + r'[^.]*\.?', '', body)
        body = body.replace(f"Source: {source_url}", "").replace(f"Source:{source_url}", "")
        body = DATE_PATTERN.sub("", body)
        # strip trailing "(source refresh date: ...)" remnants
        body = re.sub(r"\(source refresh date:[^)]*\)", "", body)
        body = re.sub(r"\s+", " ", body).strip().rstrip(".").rstrip(",").rstrip("(").strip()
        body = re.sub(r"\.\s*\.+", ".", body)

    heading = None
    if msg_type == "answer" and " — " in body[:120]:
        parts = body.split(" — ", 1)
        if len(parts[0]) < 80:
            heading = parts[0]
            body = parts[1] if len(parts) > 1 else body

    return AskResponse(
        type=msg_type,
        heading=heading,
        body=body,
        source=source,
        last_updated=last_updated,
    )


app = FastAPI(
    title="MF Facts FAQ API",
    description="RAG backend for the Groww-style HDFC mutual fund facts assistant prototype.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/amcs")
def list_amcs():
    return {
        "amcs": [
            {
                "id": "ALL",
                "label": "All AMCs",
                "schemes": [],
            },
            {
                "id": "HDFC",
                "label": "HDFC Mutual Fund",
                "schemes": [
                    "HDFC Top 100 Fund",
                    "HDFC Flexi Cap Fund",
                    "HDFC ELSS Tax Saver",
                    "HDFC Balanced Advantage Fund",
                ],
            },
            {
                "id": "Kotak",
                "label": "Kotak Mutual Fund",
                "schemes": [
                    "Kotak Flexi Cap Fund",
                    "Kotak ELSS Tax Saver Fund",
                    "Kotak Bluechip Fund",
                    "Kotak Balanced Advantage Fund",
                ],
            },
            {
                "id": "SBI",
                "label": "SBI Mutual Fund",
                "schemes": [
                    "SBI Bluechip Fund",
                    "SBI Long Term Equity Fund",
                    "SBI Flexicap Fund",
                    "SBI Balanced Advantage Fund",
                ],
            },
            {
                "id": "Nippon",
                "label": "Nippon India MF",
                "schemes": [
                    "Nippon India Large Cap Fund",
                    "Nippon India Tax Saver ELSS",
                    "Nippon India Flexi Cap Fund",
                    "Nippon India Balanced Advantage Fund",
                ],
            },
        ]
    }


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "source_count": len(SOURCE_LIST),
        "last_updated_default": date.today().isoformat(),
    }


@app.post("/api/ask", response_model=AskResponse)
def ask(payload: AskRequest):
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question is required.")
    try:
        raw = answer_question(get_qa_chain(), question)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail="Failed to generate answer.") from exc
    return parse_answer_text(raw)


if FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
else:
    @app.get("/")
    def frontend_missing():
        raise HTTPException(
            status_code=503,
            detail="Frontend not found. Copy faq-assistant-working-prototype/project to frontend/.",
        )
