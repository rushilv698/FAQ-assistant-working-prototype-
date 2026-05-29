"""Streamlit app for the Groww-style HDFC MF facts-only FAQ assistant."""

from __future__ import annotations

import base64
from html import escape
from pathlib import Path
import re

import streamlit as st

from rag_assistant import answer_question, build_qa_chain
from source_list import SOURCE_LIST

st.set_page_config(page_title="Groww", layout="wide", initial_sidebar_state="collapsed")

EXAMPLE_QUESTIONS = [
    "What is the expense ratio of HDFC Top 100 Fund direct plan?",
    "What is the lock-in period for HDFC ELSS Tax Saver?",
    "How do I download my capital gains statement?",
]

NAV_ITEMS = ["Stocks", "F&O", "Mutual Funds", "More"]
TICKER_ITEMS = [
    ("NIFTYJR", "71,858.10", -0.14),
    ("BANKNIFTY", "54,846.00", -0.01),
    ("NIFTYMIDCAP150", "22,786.20", -0.43),
]


@st.cache_data(show_spinner=False)
def asset_data_uri(filename: str) -> str:
    path = Path(__file__).parent / "assets" / filename
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def app_css() -> str:
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --groww-green: #00d09c;
        --groww-green-dark: #00b386;
        --groww-blue: #5367ff;
        --text: #44475b;
        --text-dark: #2a2e3b;
        --muted: #7c7e8c;
        --border: #e9ecf2;
        --surface: #ffffff;
        --bg: #ffffff;
        --down: #eb4b5c;
        --up: #00b386;
        --hero-bg: #f8fafc;
        --dark: #0b0b0b;
        --shadow: 0 24px 64px rgba(15, 23, 42, 0.14);
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text);
    }

    .stApp {
        background: var(--bg);
    }

    .block-container {
        max-width: 100%;
        padding: 0 !important;
    }

    #MainMenu, footer, header [data-testid="stToolbar"] {
        visibility: hidden;
    }

    .groww-page {
        background: var(--bg);
        min-height: 100vh;
    }

    .groww-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 20px;
        padding: 14px 5%;
        border-bottom: 1px solid var(--border);
        background: var(--surface);
        position: sticky;
        top: 0;
        z-index: 40;
    }

    .groww-nav-links {
        display: flex;
        align-items: center;
        gap: 28px;
        flex: 1;
        margin-left: 28px;
    }

    .groww-nav-links span {
        color: var(--muted);
        font-size: 0.95rem;
        font-weight: 500;
        cursor: default;
    }

    .groww-nav-links span.active {
        color: var(--text-dark);
        font-weight: 600;
    }

    .groww-search {
        flex: 1;
        max-width: 420px;
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 16px;
        border-radius: 8px;
        border: 1px solid var(--border);
        background: #fbfbfc;
        color: var(--muted);
        font-size: 0.92rem;
    }

    .groww-search kbd {
        margin-left: auto;
        font-size: 0.75rem;
        padding: 2px 6px;
        border-radius: 4px;
        border: 1px solid var(--border);
        background: #fff;
        color: var(--muted);
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 1.35rem;
        font-weight: 700;
        color: var(--text-dark);
        white-space: nowrap;
    }

    .brand-logo {
        width: 32px;
        height: 32px;
        border-radius: 8px;
    }

    .ticker {
        display: flex;
        align-items: center;
        gap: 28px;
        padding: 10px 5%;
        border-bottom: 1px solid var(--border);
        background: #fcfcfd;
        overflow-x: auto;
        white-space: nowrap;
        font-size: 0.82rem;
    }

    .ticker-item {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        color: var(--muted);
    }

    .ticker-item strong {
        color: var(--text-dark);
        font-weight: 600;
    }

    .ticker-change.down { color: var(--down); font-weight: 600; }
    .ticker-change.up { color: var(--up); font-weight: 600; }

    .hero {
        text-align: center;
        padding: 72px 5% 0;
        background: linear-gradient(180deg, #fff 0%, var(--hero-bg) 100%);
    }

    .hero h1 {
        font-size: clamp(2.6rem, 6vw, 4.4rem);
        font-weight: 800;
        color: var(--text-dark);
        letter-spacing: -0.03em;
        margin: 0 0 18px;
        line-height: 1.05;
    }

    .hero-sub {
        max-width: 560px;
        margin: 0 auto 28px;
        color: var(--muted);
        font-size: 1.05rem;
        line-height: 1.6;
    }

    .hero-city {
        margin-top: 24px;
        max-width: 920px;
        margin-left: auto;
        margin-right: auto;
        line-height: 0;
    }

    .hero-city svg {
        width: 100%;
        height: auto;
        max-height: 280px;
    }

    .section {
        padding: 72px 5%;
    }

    .section-title {
        text-align: center;
        font-size: clamp(1.8rem, 4vw, 2.6rem);
        font-weight: 800;
        color: var(--text-dark);
        margin: 0 0 12px;
        letter-spacing: -0.02em;
    }

    .section-sub {
        text-align: center;
        color: var(--muted);
        max-width: 520px;
        margin: 0 auto 40px;
        line-height: 1.6;
    }

    .cards-2 {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 24px;
        max-width: 980px;
        margin: 0 auto;
    }

    .product-card {
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 28px;
        background: #fff;
        min-height: 220px;
    }

    .product-card h3 {
        margin: 0 0 8px;
        font-size: 1.35rem;
        color: var(--text-dark);
    }

    .product-card p {
        color: var(--muted);
        margin: 0;
        line-height: 1.55;
    }

    .mf-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 18px;
    }

    .mf-tag {
        padding: 8px 14px;
        border-radius: 999px;
        background: #eefbf6;
        color: var(--groww-green-dark);
        font-size: 0.82rem;
        font-weight: 600;
    }

    .section-dark {
        background: var(--dark);
        color: #fff;
        padding: 80px 5%;
    }

    .section-dark .section-title,
    .section-dark .section-sub { color: #fff; }
    .section-dark .section-sub { color: #9ca3af; }

    .edu-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        max-width: 1100px;
        margin: 0 auto;
    }

    .edu-card {
        border-radius: 18px;
        padding: 28px 22px;
        min-height: 200px;
        color: #fff;
        font-weight: 700;
        font-size: 1.15rem;
        line-height: 1.4;
    }

    .edu-card.blue { background: linear-gradient(160deg, #4f7cff, #2f5fd4); }
    .edu-card.yellow { background: linear-gradient(160deg, #c8b35f, #9a8540); color: #1a1a1a; }
    .edu-card.teal { background: linear-gradient(160deg, #2db8a0, #178f7c); }

    .trust-logos {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 28px;
        max-width: 900px;
        margin: 32px auto 0;
        color: var(--muted);
        font-size: 0.88rem;
        font-weight: 600;
    }

    .footer {
        background: #f3f4f6;
        padding: 48px 5% 28px;
        border-top: 1px solid var(--border);
    }

    .footer-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 32px;
        max-width: 1000px;
        margin: 0 auto 32px;
    }

    .footer h4 {
        margin: 0 0 12px;
        color: var(--text-dark);
        font-size: 0.95rem;
    }

    .footer ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }

    .footer li {
        color: var(--muted);
        font-size: 0.88rem;
        margin-bottom: 8px;
    }

    .prototype-banner {
        text-align: center;
        padding: 14px;
        background: #fff8e6;
        color: #8a6d1d;
        font-size: 0.85rem;
        font-weight: 600;
        border-bottom: 1px solid #f0e2b8;
    }

    /* Modal overlay */
    .modal-backdrop {
        position: fixed;
        inset: 0;
        background: rgba(17, 24, 39, 0.55);
        z-index: 100;
        backdrop-filter: blur(2px);
    }

    .modal-shell {
        position: fixed;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 101;
        padding: 24px;
        pointer-events: none;
    }

    .modal-card {
        pointer-events: auto;
        display: grid;
        grid-template-columns: 1fr 1fr;
        max-width: 820px;
        width: 100%;
        min-height: 420px;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: var(--shadow);
        background: #fff;
    }

    .modal-left {
        background: var(--groww-green);
        color: #fff;
        padding: 36px 32px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        position: relative;
        overflow: hidden;
    }

    .modal-left::before {
        content: "";
        position: absolute;
        inset: 0;
        opacity: 0.35;
        background-image: url("data:image/svg+xml,%3Csvg width='120' height='120' viewBox='0 0 120 120' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 60c20-20 40-20 60 0s40 20 60 0v60H0z' fill='none' stroke='%23ffffff' stroke-width='1' opacity='.4'/%3E%3C/svg%3E");
        background-size: 120px 120px;
    }

    .modal-left h2 {
        position: relative;
        font-size: 1.65rem;
        font-weight: 800;
        line-height: 1.25;
        margin: 0;
        max-width: 200px;
    }

    .modal-left .ipo {
        position: relative;
        font-size: 1.5rem;
        font-weight: 800;
    }

    .modal-left .ipo::before {
        content: "";
        display: block;
        width: 36px;
        height: 3px;
        background: #fff;
        margin-bottom: 12px;
        border-radius: 2px;
    }

    .modal-right {
        padding: 28px 32px 24px;
        position: relative;
    }

    .modal-right h3 {
        margin: 8px 0 24px;
        font-size: 1.35rem;
        font-weight: 700;
        color: var(--text-dark);
    }

    .legal {
        margin-top: 18px;
        font-size: 0.78rem;
        color: var(--muted);
        line-height: 1.5;
    }

    .legal a {
        color: var(--text);
        text-decoration: underline;
    }

    .or-row {
        display: flex;
        align-items: center;
        gap: 14px;
        color: var(--muted);
        font-size: 0.88rem;
        margin: 18px 0;
    }

    .or-row::before, .or-row::after {
        content: "";
        flex: 1;
        height: 1px;
        background: var(--border);
    }

    /* Chat */
    .chat-page {
        min-height: 100vh;
        background: #f7f9fc;
    }

    .chat-top {
        background: #fff;
        border-bottom: 1px solid var(--border);
        padding: 14px 5%;
    }

    .chat-body {
        max-width: 860px;
        margin: 0 auto;
        padding: 28px 5% 120px;
    }

    .message-row {
        display: flex;
        margin: 16px 0;
    }

    .message-row.user { justify-content: flex-end; }

    .message {
        max-width: min(720px, 88%);
        border-radius: 16px;
        padding: 14px 16px;
        line-height: 1.6;
        font-size: 0.95rem;
    }

    .message.user {
        background: #e8faf3;
        color: var(--text-dark);
        border: 1px solid #c6f0e0;
    }

    .message.assistant {
        background: #fff;
        border: 1px solid var(--border);
        color: var(--text);
    }

    .message a {
        color: var(--groww-green-dark);
        font-weight: 600;
        text-decoration: none;
    }

    .message a:hover { text-decoration: underline; }

    .chat-pill {
        display: inline-flex;
        padding: 6px 12px;
        border-radius: 999px;
        background: #eefbf6;
        color: var(--groww-green-dark);
        font-size: 0.8rem;
        font-weight: 700;
        margin-bottom: 16px;
    }

    .chat-input-bar {
        position: fixed;
        left: 0;
        right: 0;
        bottom: 0;
        background: #fff;
        border-top: 1px solid var(--border);
        padding: 16px 5% 20px;
        z-index: 30;
    }

    .chat-input-inner {
        max-width: 860px;
        margin: 0 auto;
    }

    .chat-privacy {
        text-align: center;
        color: var(--muted);
        font-size: 0.82rem;
        margin-top: 10px;
    }

    div.stButton > button {
        min-height: 44px;
        border-radius: 8px;
        border: 1px solid var(--border);
        font-weight: 600;
        color: var(--text);
        background: #fff;
    }

    div.stButton > button[kind="primary"] {
        background: var(--groww-green);
        color: #fff;
        border-color: var(--groww-green);
    }

    div.stButton > button[kind="primary"]:hover {
        background: var(--groww-green-dark);
        border-color: var(--groww-green-dark);
    }

    .btn-login-nav {
        min-width: 130px !important;
    }

    .btn-google {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
    }

    div[data-testid="stTextInput"] input {
        border-radius: 0;
        border: none;
        border-bottom: 1px solid var(--border);
        min-height: 44px;
        background: transparent;
        padding-left: 0;
        color: var(--text-dark);
    }

    div[data-testid="stTextInput"] label {
        color: var(--muted);
        font-weight: 500;
    }

    .modal-controls {
        max-width: 820px;
        margin: 0 auto;
    }

    @media (max-width: 900px) {
        .groww-nav-links { display: none; }
        .groww-search { display: none; }
        .cards-2, .edu-grid, .modal-card { grid-template-columns: 1fr; }
        .modal-left { min-height: 140px; }
        .footer-grid { grid-template-columns: 1fr; }
    }
    </style>
    """


def init_state() -> None:
    defaults = {
        "view": "landing",
        "show_login_modal": False,
        "chat": [],
        "prefill_question": "",
        "email": "",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def get_qa_chain():
    if "qa_chain" not in st.session_state:
        with st.spinner("Preparing approved-source knowledge base..."):
            st.session_state.qa_chain = build_qa_chain()
    return st.session_state.qa_chain


def set_view(view: str) -> None:
    st.session_state.view = view
    st.rerun()


def open_login_modal() -> None:
    st.session_state.show_login_modal = True
    st.rerun()


def close_login_modal() -> None:
    st.session_state.show_login_modal = False
    st.rerun()


def enter_chat() -> None:
    st.session_state.show_login_modal = False
    st.session_state.view = "chat"
    st.rerun()


def ask_backend(question: str) -> None:
    answer = answer_question(get_qa_chain(), question.strip())
    st.session_state.chat.append({"q": question.strip(), "a": answer})
    st.session_state.prefill_question = ""
    st.rerun()


def linkify_answer(answer: str) -> str:
    safe_answer = escape(answer)
    url_pattern = re.compile(r"https?://[^\s<]+")

    def replace(match: re.Match) -> str:
        url = match.group(0).rstrip(".")
        trailing = "." if match.group(0).endswith(".") else ""
        return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{url}</a>{trailing}'

    return url_pattern.sub(replace, safe_answer)


def brand_html() -> str:
    logo_uri = asset_data_uri("groww-app-icon-hd.png")
    return f"""
    <div class="brand">
      <img class="brand-logo" src="{logo_uri}" alt="Groww" />
      <span>Groww</span>
    </div>
    """


def hero_city_svg() -> str:
    return """
    <svg viewBox="0 0 900 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="City illustration">
      <rect width="900" height="220" fill="#f4f7fb"/>
      <path d="M0 170 L900 170 L900 220 L0 220 Z" fill="#e8edf3"/>
      <rect x="80" y="95" width="70" height="75" fill="#d5dde8" rx="4"/>
      <rect x="170" y="70" width="90" height="100" fill="#c8d3e0" rx="4"/>
      <rect x="290" y="88" width="60" height="82" fill="#d5dde8" rx="4"/>
      <rect x="380" y="55" width="110" height="115" fill="#bcc9d8" rx="4"/>
      <rect x="520" y="82" width="75" height="88" fill="#d5dde8" rx="4"/>
      <rect x="620" y="62" width="95" height="108" fill="#c8d3e0" rx="4"/>
      <rect x="740" y="90" width="80" height="80" fill="#d5dde8" rx="4"/>
      <circle cx="200" cy="178" r="14" fill="#00d09c" opacity=".85"/>
      <circle cx="450" cy="178" r="14" fill="#5367ff" opacity=".75"/>
      <rect x="350" y="158" width="120" height="12" fill="#cbd5e1" rx="6"/>
      <path d="M120 170 Q200 140 280 170" stroke="#00d09c" stroke-width="3" fill="none" opacity=".5"/>
      <ellipse cx="650" cy="175" rx="28" ry="10" fill="#94a3b8" opacity=".35"/>
    </svg>
    """


def render_nav(*, login_label: str = "Login/Sign up") -> None:
    nav_links = "".join(
        f'<span class="{"active" if item == "Mutual Funds" else ""}">{item}</span>'
        for item in NAV_ITEMS
    )
    st.markdown(
        f"""
        <div class="groww-nav">
          {brand_html()}
          <div class="groww-nav-links">{nav_links}</div>
          <div class="groww-search">🔍 Search Groww.... <kbd>⌘K</kbd></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_ticker() -> None:
    items = []
    for name, value, change in TICKER_ITEMS:
        direction = "down" if change < 0 else "up"
        arrow = "↓" if change < 0 else "↑"
        items.append(
            f'<span class="ticker-item"><strong>{name}</strong> {value} '
            f'<span class="ticker-change {direction}">{arrow} {abs(change):.2f}%</span></span>'
        )
    st.markdown(f'<div class="ticker">{"".join(items)}</div>', unsafe_allow_html=True)


def render_landing() -> None:
    st.markdown('<div class="groww-page">', unsafe_allow_html=True)
    st.markdown(
        '<div class="prototype-banner">Prototype MF Facts extension — not affiliated with or supported by Groww</div>',
        unsafe_allow_html=True,
    )
    nav_row = st.columns([5, 1])
    with nav_row[0]:
        render_nav()
    with nav_row[1]:
        if st.button("Login/Sign up", key="nav_login", type="primary", use_container_width=True):
            open_login_modal()

    render_ticker()

    st.markdown(
        f"""
        <section class="hero">
          <h1>Groww your wealth</h1>
          <p class="hero-sub">
            Explore mutual fund facts from official HDFC, AMFI, and SEBI sources —
            expense ratios, exit loads, SIP minimums, and more. No investment advice.
          </p>
          <div class="hero-city">{hero_city_svg()}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("Get Started", key="hero_get_started", type="primary", use_container_width=True):
            open_login_modal()
    with c1:
        if st.button("Ask MF Facts", key="hero_ask_facts", use_container_width=True):
            enter_chat()

    st.markdown(
        """
        <section class="section">
          <h2 class="section-title">Invest in what's right for you</h2>
          <p class="section-sub">This prototype focuses on factual mutual fund Q&amp;A backed by approved public sources.</p>
          <div class="cards-2">
            <div class="product-card">
              <h3>Stocks</h3>
              <p>Direct equity investing with real-time market data. (Demo section — not active in this prototype.)</p>
            </div>
            <div class="product-card">
              <h3>Mutual Funds</h3>
              <p>Ask factual questions about supported HDFC schemes with source citations in every answer.</p>
              <div class="mf-tags">
                <span class="mf-tag">Expense ratio</span>
                <span class="mf-tag">Exit load</span>
                <span class="mf-tag">SIP minimum</span>
                <span class="mf-tag">Lock-in</span>
              </div>
            </div>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Open MF Facts Assistant", key="section_mf_cta", type="primary"):
        open_login_modal()

    st.markdown(
        """
        <section class="section-dark">
          <h2 class="section-title">Trade Futures &amp; Options Securely</h2>
          <p class="section-sub">Advanced charts, fast execution, and option chain tools. Shown for layout reference only.</p>
        </section>

        <section class="section">
          <h2 class="section-title">Build your investment knowledge</h2>
          <p class="section-sub">Educational cards mirror Groww's learning hub layout.</p>
          <div class="edu-grid">
            <div class="edu-card blue">Learn the basics of investing</div>
            <div class="edu-card yellow">Understand mutual funds in detail</div>
            <div class="edu-card teal">Master the art of stock trading</div>
          </div>
        </section>

        <section class="section">
          <h2 class="section-title">Trusted by millions of Indians</h2>
          <p class="section-sub">Answers in this prototype are limited to {count} approved official URLs.</p>
          <div class="trust-logos">
            <span>SEBI</span><span>NSE</span><span>BSE</span><span>AMFI</span><span>CDSL</span><span>NSDL</span>
          </div>
        </section>

        <footer class="footer">
          <div class="footer-grid">
            <div><h4>Products</h4><ul><li>Stocks</li><li>Mutual Funds</li><li>F&amp;O</li><li>ETFs</li></ul></div>
            <div><h4>Groww</h4><ul><li>About Us</li><li>Pricing</li><li>Blog</li><li>Careers</li></ul></div>
            <div><h4>Help &amp; Support</h4><ul><li>Help Center</li><li>Contact Us</li></ul></div>
          </div>
          <p style="text-align:center;color:#9ca3af;font-size:.78rem;margin:0;">
            Prototype for educational use. Not affiliated with Groww. {count} approved sources.
          </p>
        </footer>
        </div>
        """.format(count=len(SOURCE_LIST)),
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.show_login_modal:
        render_login_modal()


def render_login_modal() -> None:
    st.markdown('<div class="modal-backdrop"></div>', unsafe_allow_html=True)

    outer = st.columns([1, 3, 1])
    with outer[1]:
        if st.button("✕ Close", key="modal_close"):
            close_login_modal()

        panel_left, panel_right = st.columns(2)

        with panel_left:
            st.markdown(
                """
                <div class="modal-left" style="border-radius:12px 0 0 12px;min-height:360px;">
                  <h2>Simple, Free Investing.</h2>
                  <div class="ipo">IPO</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with panel_right:
            st.markdown('<div class="modal-right" style="padding-top:4px;">', unsafe_allow_html=True)
            st.markdown("### Welcome to Groww")
            if st.button("Continue with Google", key="modal_google", use_container_width=True):
                enter_chat()
            st.markdown('<div class="or-row">Or</div>', unsafe_allow_html=True)
            st.text_input("Your Email Address", key="email", placeholder="Your Email Address")
            if st.button("Continue", key="modal_continue", type="primary", use_container_width=True):
                enter_chat()
            st.markdown(
                """
                <p class="legal">
                  By proceeding, I agree to
                  <a href="#">T&amp;C</a>,
                  <a href="#">Privacy Policy</a> &amp;
                  <a href="#">Tariff Rates</a>
                </p>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)


def render_chat() -> None:
    st.markdown('<div class="chat-page">', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="chat-top">
          {brand_html()}
        </div>
        """,
        unsafe_allow_html=True,
    )

    top_cols = st.columns([1, 1, 4])
    with top_cols[0]:
        if st.button("Home", key="chat_home"):
            set_view("landing")
    with top_cols[1]:
        if st.button("New Chat", key="chat_new"):
            st.session_state.chat = []
            st.session_state.prefill_question = ""
            st.rerun()

    st.markdown('<div class="chat-body">', unsafe_allow_html=True)
    st.markdown('<span class="chat-pill">Facts-Only · No Investment Advice</span>', unsafe_allow_html=True)

    if not st.session_state.chat:
        st.markdown(
            """
            <div class="message-row">
              <div class="message assistant">
                Welcome. Ask a factual question about supported HDFC Mutual Fund schemes.
                Every answer includes one official source link.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    for item in st.session_state.chat:
        user_q = escape(item["q"])
        assistant_a = linkify_answer(item["a"])
        st.markdown(
            f"""
            <div class="message-row user"><div class="message user">{user_q}</div></div>
            <div class="message-row"><div class="message assistant">{assistant_a}</div></div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="chat-input-bar"><div class="chat-input-inner">', unsafe_allow_html=True)
    input_col, send_col = st.columns([5, 1], vertical_alignment="bottom")
    with input_col:
        question = st.text_input(
            "Ask a mutual fund question",
            value=st.session_state.prefill_question,
            placeholder="Ask about expense ratio, exit load, SIP minimum…",
            key="chat_question",
            label_visibility="collapsed",
        )
    with send_col:
        send = st.button("Send", type="primary", use_container_width=True)

    ex_cols = st.columns(3)
    for idx, example in enumerate(EXAMPLE_QUESTIONS):
        with ex_cols[idx]:
            if st.button(example, key=f"chat_ex_{idx}", use_container_width=True):
                with st.spinner("Fetching source-backed answer…"):
                    ask_backend(example)

    if send and question.strip():
        with st.spinner("Fetching source-backed answer…"):
            ask_backend(question)

    st.markdown(
        '<p class="chat-privacy">We do not store PAN, Aadhaar, account numbers, OTPs, emails, or phone numbers.</p>',
        unsafe_allow_html=True,
    )
    st.markdown("</div></div></div>", unsafe_allow_html=True)


init_state()
st.markdown(app_css(), unsafe_allow_html=True)

if st.session_state.view == "chat":
    render_chat()
else:
    render_landing()
