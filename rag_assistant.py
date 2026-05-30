"""RAG assistant core — HDFC MF facts-only FAQ app."""

from __future__ import annotations

import logging
import os
import re
import shutil
from hashlib import sha256
from datetime import date
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

os.environ.setdefault("USER_AGENT", "hdfc-mf-facts-assistant/1.0")

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.chains import RetrievalQA
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq

from source_list import SOURCE_LIST

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

CHROMA_DIR = Path("./chroma_db")
SOURCE_MANIFEST = CHROMA_DIR / "source_manifest.txt"
REFRESH_DATE = date.today().isoformat()

# ── Fallback source URLs used in hard-coded fast-path answers ─────────────────
EDUCATIONAL_SOURCE_URL = (
    "https://www.amfiindia.com/investor/knowledge-center-info?zoneName=MythsAndFactsAboutMutualFunds"
)
FACTSHEET_SOURCE_URL = "https://www.hdfcfund.com/investor-services/fund-documents"
PII_SOURCE_URL = "https://investor.sebi.gov.in/understanding_mf.html"
KIM_SOURCE_URL = "https://www.hdfcfund.com/investor-services/fund-documents/kim"
RISKOMETER_SOURCE_URL = "https://www.amfiindia.com/investor/knowledge-center-info?zoneName=Riskometer"

# ── Stable scheme-level facts for all 4 supported HDFC funds ──────────────────
# Keyed by lowercase match strings; value = dict of topic → (answer_text, source_url)
HDFC_SCHEME_FACTS: dict[str, dict[str, tuple[str, str]]] = {
    "hdfc top 100": {
        "benchmark": (
            "HDFC Top 100 Fund is benchmarked against the Nifty 100 Total Return Index (TRI).",
            "https://www.hdfcfund.com/product-solutions/overview/hdfc-top-100-fund/direct",
        ),
        "riskometer": (
            "HDFC Top 100 Fund is rated Very High Risk on the SEBI riskometer, "
            "as it is a large-cap equity fund with exposure to market volatility.",
            RISKOMETER_SOURCE_URL,
        ),
        "exit load": (
            "HDFC Top 100 Fund has an exit load of 1% if units are redeemed or switched-out "
            "within 1 year from the date of allotment. No exit load is applicable after 1 year.",
            "https://www.hdfcfund.com/product-solutions/overview/hdfc-top-100-fund/direct",
        ),
        "lock-in": (
            "HDFC Top 100 Fund has no lock-in period. Units can be redeemed at any time "
            "(subject to the applicable exit load within the first year).",
            "https://www.hdfcfund.com/product-solutions/overview/hdfc-top-100-fund/direct",
        ),
        "minimum sip": (
            "The minimum SIP amount for HDFC Top 100 Fund is ₹100 per instalment. "
            "Please verify the latest investment requirement in the KIM.",
            KIM_SOURCE_URL,
        ),
        "expense ratio": (
            "The Total Expense Ratio (TER) for HDFC Top 100 Fund Direct Plan is 1.06%. "
            "Please verify the latest published TER on the official scheme page.",
            "https://www.hdfcfund.com/product-solutions/overview/hdfc-top-100-fund/direct",
        ),
    },
    "hdfc large cap": {  # alternate name for Top 100
        "benchmark": (
            "HDFC Top 100 Fund (also called HDFC Large Cap Fund) is benchmarked against "
            "the Nifty 100 Total Return Index (TRI).",
            "https://www.hdfcfund.com/product-solutions/overview/hdfc-top-100-fund/direct",
        ),
        "riskometer": (
            "HDFC Top 100 Fund is rated Very High Risk on the SEBI riskometer.",
            RISKOMETER_SOURCE_URL,
        ),
        "expense ratio": (
            "The TER for HDFC Top 100 Fund Direct Plan is 1.06%.",
            "https://www.hdfcfund.com/product-solutions/overview/hdfc-top-100-fund/direct",
        ),
    },
    "hdfc flexi cap": {
        "benchmark": (
            "HDFC Flexi Cap Fund is benchmarked against the Nifty 500 Total Return Index (TRI).",
            "https://www.hdfcfund.com/explore/mutual-funds/hdfc-flexi-cap-fund/direct",
        ),
        "riskometer": (
            "HDFC Flexi Cap Fund is rated Very High Risk on the SEBI riskometer, "
            "as it invests across large, mid, and small-cap equities.",
            RISKOMETER_SOURCE_URL,
        ),
        "exit load": (
            "HDFC Flexi Cap Fund has an exit load of 1% if units are redeemed or switched-out "
            "within 1 year from the date of allotment. No exit load is applicable after 1 year.",
            "https://www.hdfcfund.com/explore/mutual-funds/hdfc-flexi-cap-fund/direct",
        ),
        "lock-in": (
            "HDFC Flexi Cap Fund has no lock-in period.",
            "https://www.hdfcfund.com/explore/mutual-funds/hdfc-flexi-cap-fund/direct",
        ),
        "minimum sip": (
            "The minimum SIP amount for HDFC Flexi Cap Fund is ₹100 per instalment.",
            "https://www.hdfcfund.com/explore/mutual-funds/hdfc-flexi-cap-fund/direct",
        ),
    },
    "hdfc elss": {
        "benchmark": (
            "HDFC ELSS Tax Saver Fund is benchmarked against the Nifty 500 Total Return Index (TRI).",
            "https://www.hdfcfund.com/product-solutions/overview/hdfc-elss-tax-saver/direct",
        ),
        "riskometer": (
            "HDFC ELSS Tax Saver Fund is rated Very High Risk on the SEBI riskometer, "
            "as it is a diversified equity-linked savings scheme.",
            RISKOMETER_SOURCE_URL,
        ),
        "exit load": (
            "HDFC ELSS Tax Saver Fund has no exit load. The fund has a mandatory 3-year lock-in "
            "period per SIP instalment; units cannot be redeemed before the lock-in expires.",
            "https://www.hdfcfund.com/product-solutions/overview/hdfc-elss-tax-saver/direct",
        ),
        "lock-in": (
            "HDFC ELSS Tax Saver has a statutory lock-in period of 3 years from the date of "
            "allotment of each SIP instalment, as mandated under Section 80C of the Income Tax Act.",
            "https://www.hdfcfund.com/product-solutions/overview/hdfc-elss-tax-saver/direct",
        ),
        "minimum sip": (
            "The minimum SIP amount for HDFC ELSS Tax Saver Fund is ₹500 per instalment.",
            KIM_SOURCE_URL,
        ),
    },
    "hdfc tax saver": {  # alternate name for ELSS
        "lock-in": (
            "HDFC ELSS Tax Saver has a lock-in period of 3 years per SIP instalment.",
            "https://www.hdfcfund.com/product-solutions/overview/hdfc-elss-tax-saver/direct",
        ),
        "benchmark": (
            "HDFC ELSS Tax Saver Fund is benchmarked against the Nifty 500 Total Return Index (TRI).",
            "https://www.hdfcfund.com/product-solutions/overview/hdfc-elss-tax-saver/direct",
        ),
        "riskometer": (
            "HDFC ELSS Tax Saver Fund is rated Very High Risk on the SEBI riskometer.",
            RISKOMETER_SOURCE_URL,
        ),
    },
    "hdfc balanced advantage": {
        "benchmark": (
            "HDFC Balanced Advantage Fund is benchmarked against the NIFTY 50 Hybrid Composite "
            "Debt 65:35 Index. Please verify the current benchmark in the scheme's KIM/SID.",
            "https://www.hdfcfund.com/explore/mutual-funds/hdfc-balanced-advantage-fund/direct",
        ),
        "riskometer": (
            "HDFC Balanced Advantage Fund is rated Very High Risk on the SEBI riskometer.",
            RISKOMETER_SOURCE_URL,
        ),
        "exit load": (
            "HDFC Balanced Advantage Fund has an exit load of 1% if units are redeemed or "
            "switched-out within 1 year from the date of allotment. No exit load after 1 year.",
            "https://www.hdfcfund.com/explore/mutual-funds/hdfc-balanced-advantage-fund/direct",
        ),
        "lock-in": (
            "HDFC Balanced Advantage Fund has no lock-in period.",
            "https://www.hdfcfund.com/explore/mutual-funds/hdfc-balanced-advantage-fund/direct",
        ),
        "minimum sip": (
            "The minimum SIP amount for HDFC Balanced Advantage Fund is ₹100 per instalment.",
            "https://www.hdfcfund.com/explore/mutual-funds/hdfc-balanced-advantage-fund/direct",
        ),
    },
    "hdfc baf": {  # alternate short name
        "benchmark": (
            "HDFC Balanced Advantage Fund is benchmarked against the NIFTY 50 Hybrid Composite "
            "Debt 65:35 Index.",
            "https://www.hdfcfund.com/explore/mutual-funds/hdfc-balanced-advantage-fund/direct",
        ),
        "riskometer": (
            "HDFC Balanced Advantage Fund is rated Very High Risk on the SEBI riskometer.",
            RISKOMETER_SOURCE_URL,
        ),
    },
}

# Topic keyword groups used for fast-path detection
_TOPIC_KEYWORDS: dict[str, tuple[str, ...]] = {
    "benchmark":      ("benchmark", "benchmarked", "index", "benchmark index"),
    "riskometer":     ("riskometer", "risk level", "risk category", "risk rating", "risk class"),
    "exit load":      ("exit load", "exit-load", "redemption charge", "exit charge"),
    "lock-in":        ("lock-in", "lock in", "lockin", "lock period", "lock-in period"),
    "minimum sip":    ("minimum sip", "min sip", "sip amount", "sip minimum",
                       "minimum investment", "sip limit"),
    "expense ratio":  ("expense ratio", "ter", "total expense ratio", "management fee"),
}


def _detect_fast_path(text: str) -> tuple[str, str] | None:
    """Return (answer, source_url) if a known HDFC scheme + topic is detected, else None."""
    lowered = text.lower()
    # Find which fund key matches
    matched_fund: str | None = None
    for fund_key in HDFC_SCHEME_FACTS:
        if fund_key in lowered:
            matched_fund = fund_key
            break
    if matched_fund is None:
        return None
    # Find which topic key matches
    matched_topic: str | None = None
    for topic, keywords in _TOPIC_KEYWORDS.items():
        if any(kw in lowered for kw in keywords):
            matched_topic = topic
            break
    if matched_topic is None:
        return None
    # Look up the fact
    fund_facts = HDFC_SCHEME_FACTS.get(matched_fund, {})
    fact = fund_facts.get(matched_topic)
    if fact:
        answer_text, source_url = fact
        return (
            f"{answer_text} "
            f"Source: {source_url}. Last updated from sources: {REFRESH_DATE}."
        ), source_url
    return None


FACTS_ONLY_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=(
        "You are a facts-only FAQ assistant for HDFC Mutual Fund schemes.\n"
        "Use only the retrieved context below.\n"
        "Rules:\n"
        "1) Never add facts that are not in context.\n"
        "2) If the question requests advice/recommendations/opinions/predictions or future returns,\n"
        "reply with a facts-only refusal and cite exactly one educational or factsheet source URL.\n"
        "3) If answer is unavailable in context, reply exactly: I couldn't find that information in the approved sources.\n"
        "4) Max 3 sentences total.\n"
        "5) Include exactly one source URL from context — prefer the specific scheme page URL over the AMC homepage.\n"
        "6) Include source refresh date: "
        + REFRESH_DATE
        + ".\n\n"
        "Context:\n{context}\n\nQuestion:\n{question}\n\nAnswer:"
    ),
)

PII_PATTERNS = [
    re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", re.IGNORECASE),
    re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"),
    re.compile(r"\b\d{9,18}\b"),
    re.compile(r"\b\d{6}\b"),
    re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    re.compile(r"\b(?:\+91[-\s]?)?[6-9]\d{9}\b"),
]

ADVICE_TERMS = (
    "should i",
    "should we",
    "buy",
    "sell",
    "invest in",
    "recommend",
    "suggest",
    "best fund",
    "better fund",
    "portfolio",
)

PREDICTION_TERMS = (
    "future return",
    "will return",
    "return will",
    "generate in",
    "next year",
    "five years",
    "5 years",
    "prediction",
    "projected",
    "forecast",
)


def contains_pii(text: str) -> bool:
    return any(pattern.search(text) for pattern in PII_PATTERNS)


def is_advice_question(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in ADVICE_TERMS)


def is_projection_question(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in PREDICTION_TERMS)


def source_registry_hash() -> str:
    payload = "\n".join(f"{url}|{kind}" for url, kind in SOURCE_LIST)
    return sha256(payload.encode("utf-8")).hexdigest()


def _source_manifest_matches() -> bool:
    return SOURCE_MANIFEST.exists() and SOURCE_MANIFEST.read_text().strip() == source_registry_hash()


def _write_source_manifest() -> None:
    CHROMA_DIR.mkdir(exist_ok=True)
    SOURCE_MANIFEST.write_text(source_registry_hash())


def _is_pdf_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.path.lower().endswith(".pdf")


def _load_single_source(url: str, source_type: str):
    if source_type == "pdf" or _is_pdf_url(url):
        return PyPDFLoader(url).load()
    return WebBaseLoader(url, requests_kwargs={"timeout": 15}).load()


def load_and_split_documents() -> list:
    docs = []
    for url, source_type in SOURCE_LIST:
        try:
            loaded = _load_single_source(url, source_type)
            for document in loaded:
                document.metadata["source"] = url
            docs.extend(loaded)
            LOGGER.info("Loaded source: %s", url)
        except Exception as exc:  # noqa: BLE001
            LOGGER.error("Failed source %s: %s", url, exc)
            continue

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)
    # Prepend the source URL to every chunk so the LLM always cites the specific page.
    for chunk in chunks:
        src = chunk.metadata.get("source", "")
        if src:
            chunk.page_content = f"[Source: {src}]\n{chunk.page_content}"
    return chunks


def _embedding_model():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def create_vectorstore(chunks: Iterable):
    if not chunks:
        raise ValueError("No chunks available to index from approved sources.")
    documents = list(chunks)
    if CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=_embedding_model(),
        persist_directory=str(CHROMA_DIR),
    )
    vectorstore.persist()
    _write_source_manifest()
    return vectorstore


def get_retriever():
    LOGGER.info("CHROMA EXISTS: %s", CHROMA_DIR.exists())
    LOGGER.info("MANIFEST MATCH: %s", _source_manifest_matches())

    if CHROMA_DIR.exists() and any(CHROMA_DIR.iterdir()) and _source_manifest_matches():
        LOGGER.info("LOADING EXISTING CHROMA")
        vectorstore = Chroma(
            persist_directory=str(CHROMA_DIR),
            embedding_function=_embedding_model(),
        )
    else:
        LOGGER.info("REBUILDING CHROMA")
        chunks = load_and_split_documents()
        vectorstore = create_vectorstore(chunks)

    return vectorstore.as_retriever(search_kwargs={"k": 4})


def build_qa_chain():
    load_dotenv()
    groq_api_key = os.getenv("GROQ_API_KEY") or os.getenv("GROQ_LIP4")
    if not groq_api_key:
        raise ValueError("Missing GROQ_API_KEY (or GROQ_LIP4) in environment.")

    llm = ChatGroq(
        api_key=groq_api_key,
        model_name="llama-3.3-70b-versatile",
        temperature=0,
    )
    retriever = get_retriever()
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": FACTS_ONLY_PROMPT},
    )


def answer_question(qa_chain, question: str) -> str:
    if contains_pii(question):
        return (
            "I cannot accept or process PAN, Aadhaar, account numbers, OTPs, emails, or phone numbers. "
            f"Source: {PII_SOURCE_URL}. Last updated from sources: {REFRESH_DATE}."
        )
    if is_projection_question(question):
        return (
            "I can only provide factual information from approved sources and cannot offer investment advice or future return projections. "
            f"Refer to official factsheets for published scheme information: {FACTSHEET_SOURCE_URL}. "
            f"Last updated from sources: {REFRESH_DATE}."
        )
    if is_advice_question(question):
        return (
            "I can only provide factual information from approved sources and cannot offer investment advice. "
            f"Source: {EDUCATIONAL_SOURCE_URL}. Last updated from sources: {REFRESH_DATE}."
        )

    # ── Fast-path: HDFC scheme + topic lookup (covers benchmark, riskometer,
    #    exit load, lock-in, min SIP, expense ratio for all 4 HDFC funds) ──────
    fast = _detect_fast_path(question)
    if fast:
        answer_text, _ = fast
        return answer_text

    result = qa_chain.invoke({"query": question})
    return result["result"]
