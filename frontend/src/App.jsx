import { useState, useEffect } from "react";
import "./App.css";
import ResultPanel from "./components/ResultPanel";
import HistoryPanel from "./components/HistoryPanel";

function App() {
  const [prompt, setPrompt] = useState("");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [dark, setDark] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const [apiStatus, setApiStatus] = useState("checking"); 
  // checking | online | offline

  useEffect(() => {
    document.body.className = dark ? "dark-mode" : "light-mode";
  }, [dark]);

  // API HEALTH CHECK
  async function checkAPI() {
    try {
      const res = await fetch("http://127.0.0.1:9000/");
      setApiStatus(res.ok ? "online" : "offline");
    } catch {
      setApiStatus("offline");
    }
  }

  useEffect(() => {
    checkAPI();
    const timer = setInterval(checkAPI, 5000);
    return () => clearInterval(timer);
  }, []);

  // ANALYZE PROMPT
  async function analyzePrompt() {
    setLoading(true);
    setResult(null);

    try {
      const res = await fetch("http://127.0.0.1:9000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });

      const data = await res.json();
      setResult(data);

      // Save to history
      setHistory((prev) => [
        {
          prompt,
          safe: data.safe ?? data.analysis?.final_safe ?? false,
          full: data,
        },
        ...prev,
      ]);

    } catch {
      setResult({ error: "Backend unreachable" });
    }

    setLoading(false);
  }

  return (
    <div className="wrapper">

      {/* Header */}
      <header className="header fadeIn">
        <h1 className="logo">PromptGuard</h1>

        <div className="rightControls">

          {/* History Button */}
          <button className="themeToggle" onClick={() => setSidebarOpen(true)}>
            📜 History
          </button>

          {/* API Dot */}
          <div className={`apiDot ${apiStatus}`} title={`API: ${apiStatus}`} />

          {/* Theme Toggle */}
          <button className="themeToggle" onClick={() => setDark(!dark)}>
            {dark ? "🌞 Light" : "🌙 Dark"}
          </button>
        </div>
      </header>

      {/* Main Card */}
      <div className="card fadeInUp">
        <textarea
          className="promptBox"
          placeholder="Type your prompt…"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />

        <button
          className="analyzeBtn"
          onClick={analyzePrompt}
          disabled={loading}
        >
          {loading ? "Analyzing…" : "Analyze"}
        </button>

        <ResultPanel loading={loading} result={result} />
      </div>

      {/* Sidebar */}
      <HistoryPanel
        history={history}
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onSelect={(item) => {
          setPrompt(item.prompt);
          setResult(item.full);
          setSidebarOpen(false);
        }}
      />
    </div>
  );
}

export default App;
