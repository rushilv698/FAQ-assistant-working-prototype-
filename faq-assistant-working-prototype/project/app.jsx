// ===================== APP ROOT + ROUTING =====================
function App() {
  const [screen, setScreen] = React.useState("landing"); // landing | login | chat
  const [pending, setPending] = React.useState(null); // question to seed into chat
  const [seed, setSeed] = React.useState(null);
  const [theme, setTheme] = React.useState(() => {
    try { return localStorage.getItem("mf-faq-theme") || "light"; } catch (e) { return "light"; }
  });

  React.useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    try { localStorage.setItem("mf-faq-theme", theme); } catch (e) {}
  }, [theme]);

  const toggleTheme = () => setTheme((t) => (t === "dark" ? "light" : "dark"));

  const goHome = () => {
    setSeed(null);
    setPending(null);
    setScreen("landing");
  };

  const goLogin = (question) => {
    if (typeof question === "string") setPending(question);
    else setPending(null);
    setScreen("login");
  };

  const enterChat = () => {
    setSeed(pending);
    setScreen("chat");
  };

  const newChat = () => {
    setSeed(null);
    setPending(null);
    setScreen("chat-reset");
    setTimeout(() => setScreen("chat"), 0);
  };

  const themeProps = { theme, onToggleTheme: toggleTheme, onHome: goHome };

  if (screen === "landing") {
    return (
      <Landing
        onAsk={(q) => goLogin(typeof q === "string" ? q : undefined)}
        onExamples={() => goLogin()}
        onLogin={() => goLogin()}
        {...themeProps}
      />
    );
  }
  if (screen === "login") {
    return <Login onContinue={enterChat} onBack={() => setScreen("landing")} {...themeProps} />;
  }
  if (screen === "chat-reset") {
    return <div className="screen chat" />;
  }
  return <Chat key={seed || "blank"} seedQuestion={seed} onNewChat={newChat} {...themeProps} />;
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
