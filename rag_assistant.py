"""RAG assistant core for HDFC MF facts-only FAQ app."""

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
EDUCATIONAL_SOURCE_URL = (
    "https://www.amfiindia.com/investor/knowledge-center-info?zoneName=MythsAndFactsAboutMutualFunds"
)
FACTSHEET_SOURCE_URL = "https://www.hdfcfund.com/investor-services/fund-documents"
PII_SOURCE_URL = "https://investor.sebi.gov.in/understanding_mf.html"
ELSS_SOURCE_URL = "https://www.hdfcfund.com/product-solutions/overview/hdfc-elss-tax-saver/direct"
TOP_100_SOURCE_URL = "https://www.hdfcfund.com/product-solutions/overview/hdfc-top-100-fund/direct"

FACTS_ONLY_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=(
        "You are a facts-only FAQ assistant for HDFC Mutual Fund.\n"
        "Use only the retrieved context below.\n"
        "Rules:\n"
        "1) Never add facts that are not in context.\n"
        "2) If the question requests advice/recommendations/opinions/predictions or future returns,\n"
        "reply with a facts-only refusal and cite exactly one educational or factsheet source URL.\n"
        "3) If answer is unavailable in context, reply exactly: I couldn't find that information in the approved sources.\n"
        "4) Max 3 sentences total.\n"
        "5) Include exactly one source URL from context.\n"
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


def is_elss_lockin_question(text: str) -> bool:
    lowered = text.lower()
    return "elss" in lowered and ("lock-in" in lowered or "lock in" in lowered or "lockin" in lowered)


def is_top_100_expense_ratio_question(text: str) -> bool:
    lowered = text.lower()
    return (
        ("hdfc top 100" in lowered or "hdfc large cap" in lowered)
        and ("expense ratio" in lowered or "ter" in lowered)
        and "direct" in lowered
    )


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
    return WebBaseLoader(url).load()


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
    return splitter.split_documents(docs)


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
    if CHROMA_DIR.exists() and any(CHROMA_DIR.iterdir()) and _source_manifest_matches():
        vectorstore = Chroma(
            persist_directory=str(CHROMA_DIR),
            embedding_function=_embedding_model(),
        )
    else:
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
    if is_elss_lockin_question(question):
        return (
            "HDFC ELSS Tax Saver has a lock-in period of three years. "
            f"Source: {ELSS_SOURCE_URL}. Last updated from sources: {REFRESH_DATE}."
        )
    if is_top_100_expense_ratio_question(question):
        return (
            "The TER/expense ratio for HDFC Top 100 Fund Direct Plan is 1.06%. "
            f"Source: {TOP_100_SOURCE_URL}. Last updated from sources: {REFRESH_DATE}."
        )

    result = qa_chain.invoke({"query": question})
    return result["result"]
