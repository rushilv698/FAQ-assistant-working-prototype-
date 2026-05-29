// ===================== CHAT (FAQ ASSISTANT) SCREEN =====================

const CHIPS = [
  "Expense Ratio",
  "Exit Load",
  "Minimum SIP",
  "Riskometer",
  "Benchmark",
  "Lock-in Period",
  "Capital Gains Statement",
];

// Per-chip question templates; fund is substituted for all except service questions.
const CHIP_TEMPLATES = {
  "Expense Ratio":           (fund) => `What is the expense ratio of ${fund} direct plan?`,
  "Exit Load":               (fund) => `What is the exit load of ${fund}?`,
  "Minimum SIP":             (fund) => `What is the minimum SIP amount for ${fund}?`,
  "Riskometer":              (fund) => `What is the riskometer level of ${fund}?`,
  "Benchmark":               (fund) => `What is the benchmark index of ${fund}?`,
  "Lock-in Period":          (fund) => `What is the lock-in period for ${fund}?`,
  "Capital Gains Statement": ()     => "How do I download my capital gains statement for mutual funds?",
};

// Per-AMC sample questions shown in the empty state and on landing.
const AMC_DATA = {
  ALL: {
    label: "All AMCs",
    chipFund: "HDFC Flexi Cap Fund",
    examples: [
      "What is the expense ratio of HDFC Top 100 Fund direct plan?",
      "What is the lock-in period for HDFC ELSS Tax Saver?",
      "What is the exit load of SBI Bluechip Fund?",
      "What is the minimum SIP for Kotak Flexi Cap Fund?",
      "What is the benchmark of Nippon India Large Cap Fund?",
      "How do I download my capital gains statement for mutual funds?",
    ],
  },
  HDFC: {
    label: "HDFC",
    chipFund: "HDFC Flexi Cap Fund",
    examples: [
      "What is the expense ratio of HDFC Top 100 Fund direct plan?",
      "What is the lock-in period for HDFC ELSS Tax Saver?",
      "What is the exit load of HDFC Flexi Cap Fund direct plan?",
      "What is the minimum SIP for HDFC Balanced Advantage Fund?",
      "What is the benchmark of HDFC Flexi Cap Fund?",
      "How do I download my capital gains statement for mutual funds?",
    ],
  },
  Kotak: {
    label: "Kotak",
    chipFund: "Kotak Flexi Cap Fund",
    examples: [
      "What is the expense ratio of Kotak Flexi Cap Fund direct plan?",
      "What is the lock-in period for Kotak ELSS Tax Saver Fund?",
      "What is the exit load of Kotak Bluechip Fund?",
      "What is the minimum SIP for Kotak Balanced Advantage Fund?",
      "What is the benchmark of Kotak Flexi Cap Fund?",
      "How do I download my capital gains statement for mutual funds?",
    ],
  },
  SBI: {
    label: "SBI",
    chipFund: "SBI Bluechip Fund",
    examples: [
      "What is the expense ratio of SBI Bluechip Fund direct plan?",
      "What is the lock-in period for SBI Long Term Equity Fund?",
      "What is the exit load of SBI Flexicap Fund?",
      "What is the minimum SIP for SBI Balanced Advantage Fund?",
      "What is the benchmark of SBI Bluechip Fund?",
      "How do I download my capital gains statement for mutual funds?",
    ],
  },
  Nippon: {
    label: "Nippon",
    chipFund: "Nippon India Large Cap Fund",
    examples: [
      "What is the expense ratio of Nippon India Large Cap Fund direct plan?",
      "What is the lock-in period for Nippon India Tax Saver ELSS Fund?",
      "What is the exit load of Nippon India Flexi Cap Fund?",
      "What is the minimum SIP for Nippon India Balanced Advantage Fund?",
      "What is the benchmark of Nippon India Large Cap Fund?",
      "How do I download my capital gains statement for mutual funds?",
    ],
  },
};

const AMC_KEYS = ["ALL", "HDFC", "Kotak", "SBI", "Nippon"];

function timeNow() {
  return new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", hour12: true });
}

async function askBackend(question) {
  const base = window.KB?.API_BASE ?? "";
  const res = await fetch(`${base}/api/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.detail || res.statusText || "Request failed");
  }
  return data;
}

function SourceCard({ source, lastUpdated }) {
  const updated = lastUpdated || window.KB?.LAST_UPDATED || "";
  return (
    <div className="source-card">
      <div className="source-line">
        <span className="source-key">Source:</span>
      </div>
      <a className="source-link" href={source.url} target="_blank" rel="noreferrer">
        <span>{source.label}</span>
        <I.External s={13} c="var(--blue)" />
      </a>
      <div className="source-meta">Last updated from sources: {updated}</div>
    </div>
  );
}

function UserMsg({ text, time }) {
  return (
    <div className="row user-row">
      <div className="bubble user-bubble">
        <div className="bubble-text">{text}</div>
        <div className="bubble-time">
          <span>{time}</span>
          <I.Check2 s={13} c="var(--green-dark)" />
        </div>
      </div>
      <div className="avatar user-avatar"><I.User s={17} c="var(--green-dark)" /></div>
    </div>
  );
}

function BotAvatar() {
  return (
    <div className="avatar bot-avatar">
      <img src="assets/groww-logo.png" alt="" width={26} height={26} />
    </div>
  );
}

function AnswerMsg({ msg }) {
  return (
    <div className="row bot-row">
      <BotAvatar />
      <div className="bubble bot-bubble">
        {msg.type === "answer" && (
          <React.Fragment>
            {msg.heading && <div className="ans-heading">{msg.heading}</div>}
            <div className="ans-body">{msg.body}</div>
            {msg.source && <SourceCard source={msg.source} lastUpdated={msg.last_updated} />}
          </React.Fragment>
        )}

        {msg.type === "refusal" && (
          <React.Fragment>
            <div className="refusal-tag">
              <I.NoAdvice s={14} c="var(--error)" />
              <span>Investment advice — not provided</span>
            </div>
            <div className="ans-body">{msg.body}</div>
            {msg.source && <SourceCard source={msg.source} lastUpdated={msg.last_updated} />}
          </React.Fragment>
        )}

        {msg.type === "error" && (
          <React.Fragment>
            <div className="ans-body">
              {msg.body ||
                "I couldn't find this in the approved AMC, AMFI or SEBI sources. Try rephrasing, or ask about expense ratio, exit load, benchmark, riskometer, lock-in or minimum SIP for a supported scheme."}
            </div>
            {msg.source && <SourceCard source={msg.source} lastUpdated={msg.last_updated} />}
          </React.Fragment>
        )}
      </div>
    </div>
  );
}

function Typing() {
  return (
    <div className="row bot-row">
      <BotAvatar />
      <div className="bubble bot-bubble typing-bubble">
        <div className="dots"><span></span><span></span><span></span></div>
        <span className="typing-text">Searching official sources…</span>
      </div>
    </div>
  );
}

function AmcSelector({ selected, onSelect }) {
  return (
    <div className="amc-selector">
      {AMC_KEYS.map((key) => (
        <button
          key={key}
          className={"amc-pill" + (selected === key ? " amc-pill-active" : "")}
          onClick={() => onSelect(key)}
        >
          {AMC_DATA[key].label}
        </button>
      ))}
    </div>
  );
}

function EmptyState({ onPick, selectedAmc }) {
  const amc = AMC_DATA[selectedAmc] || AMC_DATA.ALL;
  return (
    <div className="empty-state">
      <div className="empty-logo">
        <img src="assets/groww-logo.png" alt="" width={48} height={48} />
      </div>
      <h2 className="empty-title">Ask anything about mutual funds</h2>
      <p className="empty-sub">
        Factual answers on expense ratios, exit loads, benchmarks, riskometers, lock-ins and SIPs —
        every one backed by an official AMC, AMFI or SEBI source.
      </p>
      <div className="empty-examples">
        {amc.examples.map((q, i) => (
          <button className="empty-ex" key={i} onClick={() => onPick(q)}>
            <span>{q}</span>
            <I.Arrow s={16} c="var(--green)" />
          </button>
        ))}
      </div>
    </div>
  );
}

function Chat({ seedQuestion, onNewChat, onHome, theme, onToggleTheme }) {
  const [messages, setMessages] = React.useState([]);
  const [input, setInput] = React.useState("");
  const [busy, setBusy] = React.useState(false);
  const [selectedAmc, setSelectedAmc] = React.useState("ALL");
  const scrollRef = React.useRef(null);
  const seededRef = React.useRef(false);

  const scrollToBottom = () => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  };

  React.useEffect(() => { scrollToBottom(); }, [messages, busy]);

  const submit = React.useCallback(async (text) => {
    const q = (text || "").trim();
    if (!q || busy) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", text: q, time: timeNow() }]);
    setBusy(true);

    try {
      const result = await askBackend(q);
      setMessages((m) => [...m, { role: "bot", ...result }]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        {
          role: "bot",
          type: "error",
          body:
            "Unable to reach the FAQ assistant backend. Start the API with: uvicorn api:app --reload --port 8000",
        },
      ]);
    } finally {
      setBusy(false);
    }
  }, [busy]);

  React.useEffect(() => {
    if (seedQuestion && !seededRef.current) {
      seededRef.current = true;
      submit(seedQuestion);
    }
  }, [seedQuestion, submit]);

  const handleChip = (chip) => {
    const amc = AMC_DATA[selectedAmc] || AMC_DATA.ALL;
    const template = CHIP_TEMPLATES[chip];
    if (template) {
      setInput(template(amc.chipFund));
    }
  };

  return (
    <div className="screen chat">
      <header className="chat-header">
        <Logo size={30} textSize={21} onClick={onHome} />
        <div className="nav-right">
          <ThemeToggle theme={theme} onToggle={onToggleTheme} />
          <button className="btn-newchat" onClick={onNewChat}>
            <I.NewChat s={17} c="var(--green)" />
            <span>New Chat</span>
          </button>
        </div>
      </header>

      <div className="chat-banner">
        <FactsBadge />
        <AmcSelector selected={selectedAmc} onSelect={setSelectedAmc} />
        <div className="chips-row">
          {CHIPS.map((c, i) => (
            <button className="chip" key={i} onClick={() => handleChip(c)}>{c}</button>
          ))}
        </div>
      </div>

      <div className="chat-scroll" ref={scrollRef}>
        <div className="chat-inner">
          {messages.length === 0 && !busy && (
            <EmptyState onPick={submit} selectedAmc={selectedAmc} />
          )}
          {messages.map((m, i) =>
            m.role === "user" ? (
              <UserMsg key={i} text={m.text} time={m.time} />
            ) : (
              <AnswerMsg key={i} msg={m} />
            )
          )}
          {busy && <Typing />}
        </div>
      </div>

      <div className="chat-input-wrap">
        <div className="chat-input">
          <input
            type="text"
            placeholder="Ask a mutual fund question…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && submit(input)}
            disabled={busy}
          />
          <button className="send-btn" disabled={!input.trim() || busy} onClick={() => submit(input)}>
            <I.Send s={19} c="#fff" />
          </button>
        </div>
        <div className="chat-foot-note">
          <I.Lock s={13} c="var(--faint)" />
          <span>We do not store or collect any personal or financial information.</span>
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { Chat });
