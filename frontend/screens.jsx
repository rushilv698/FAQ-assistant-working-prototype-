// ===================== LANDING + LOGIN SCREENS =====================

function Landing({ onAsk, onLogin, onExamples, onHome, theme, onToggleTheme }) {
  const trust = [
    { icon: <I.Shield s={20} c="var(--green-dark)" />, label: "Official Sources Only" },
    { icon: <I.Doc s={20} c="var(--green-dark)" />, label: "Facts-Only Responses" },
    { icon: <I.Link s={20} c="var(--green-dark)" />, label: "Source in Every Answer" },
    { icon: <I.NoAdvice s={20} c="var(--error)" />, label: "No Investment Advice", danger: true },
  ];

  const popular = [
    "What is the expense ratio of HDFC Top 100 Fund direct plan?",
    "What is the lock-in period for SBI Long Term Equity Fund?",
    "What is the exit load of Kotak Flexi Cap Fund?",
    "What is the minimum SIP for Nippon India Large Cap Fund?",
    "How do I download my capital gains statement for mutual funds?",
  ];

  return (
    <div className="screen landing">
      <header className="nav">
        <Logo size={30} textSize={21} onClick={onHome} />
        <div className="nav-right">
          <ThemeToggle theme={theme} onToggle={onToggleTheme} />
          <button className="btn-outline btn-login-top" onClick={onLogin}>Login</button>
        </div>
      </header>

      <main className="landing-main">
        <FactsBadge />

        <h1 className="hero-title">
          Get Mutual Fund<br />Facts in Seconds.<br />
          <span className="accent">Not Opinions.</span>
        </h1>

        <p className="hero-sub">
          Ask about expense ratios, exit loads, SIP minimums, lock-ins, riskometers and benchmarks.
          Every answer comes from official AMC, AMFI or SEBI sources — with a citation.
        </p>

        <div className="hero-cta">
          <button className="btn-primary btn-lg" onClick={onAsk}>
            <span>Ask a Question</span>
            <I.Arrow s={18} />
          </button>
          <button className="btn-outline btn-lg" onClick={onExamples}>
            <I.List s={17} c="var(--secondary)" />
            <span>See Example Questions</span>
          </button>
        </div>

        <div className="trust-row">
          {trust.map((t, i) => (
            <div className="trust-item" key={i}>
              <div className={"trust-icon" + (t.danger ? " danger" : "")}>{t.icon}</div>
              <div className="trust-label">{t.label}</div>
            </div>
          ))}
        </div>

        <div className="popular">
          <h3 className="popular-title">Try these popular questions</h3>
          <div className="popular-list">
            {popular.map((q, i) => (
              <button className="popular-card" key={i} onClick={() => onAsk(q)}>
                <span>{q}</span>
                <I.Chevron s={18} c="var(--faint)" />
              </button>
            ))}
          </div>
        </div>
      </main>

      <footer className="landing-foot">
        <ProtoNote />
      </footer>
    </div>
  );
}

function Login({ onContinue, onBack, onHome, theme, onToggleTheme }) {
  const [mobile, setMobile] = React.useState("");
  const valid = mobile.replace(/\D/g, "").length === 10;

  return (
    <div className="screen login">
      <header className="nav">
        <button className="link-back" onClick={onBack}>← Back</button>
        <ThemeToggle theme={theme} onToggle={onToggleTheme} />
      </header>

      <main className="login-main">
        <div className="login-card">
          <button className="login-logo logo-btn" onClick={onHome} aria-label="Go to home" title="Home" style={{ cursor: "pointer" }}>
            <img src="assets/groww-logo.png" alt="Groww" width={56} height={56} />
            <span>Groww</span>
          </button>

          <h2 className="login-title">Welcome back</h2>
          <p className="login-sub">Login to access Groww Mutual Fund FAQs (Facts-Only Q&amp;A)</p>

          <label className="field-label">Mobile number</label>
          <div className={"phone-field" + (valid ? " ok" : "")}>
            <div className="phone-cc">
              <I.Indian s={22} />
              <span>+91</span>
              <I.Chevron s={14} c="var(--faint)" />
            </div>
            <input
              type="tel"
              inputMode="numeric"
              maxLength={10}
              placeholder="Enter mobile number"
              value={mobile}
              onChange={(e) => setMobile(e.target.value.replace(/\D/g, "").slice(0, 10))}
              onKeyDown={(e) => e.key === "Enter" && valid && onContinue()}
            />
          </div>

          <button className="btn-primary btn-block" disabled={!valid} onClick={onContinue}>
            Continue
          </button>

          <div className="or-divider"><span>or</span></div>

          <button className="btn-google" onClick={onContinue}>
            <I.Google s={18} />
            <span>Continue with Google</span>
          </button>

          <div className="secure-note">
            <I.Lock s={13} c="var(--faint)" />
            <span>Secure login. We never share your data.</span>
          </div>
        </div>
      </main>

      <footer className="landing-foot">
        <ProtoNote />
      </footer>
    </div>
  );
}

Object.assign(window, { Landing, Login });
