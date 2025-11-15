import { useState } from "react";
import "./ResultPanel.css";

function ResultPanel({ result }) {
  const [showJSON, setShowJSON] = useState(false);

  if (!result) return null;

  const safeFlag =
    result.safe ??
    result.analysis?.final_safe ??
    false;

  const reasons =
    result.analysis?.reason || result.reason || [];

  const sanitized =
    result.analysis?.sanitized || result.sanitized;

  const semanticScore =
    result.analysis?.semantic_score ?? result.semantic_score ?? 0;

  return (
    <div className="resultPanel fadeInUp">

      {/* Safety Badge */}
      <div className={`rpBadge ${safeFlag ? "safe" : "unsafe"}`}>
        {safeFlag ? "SAFE ✔" : "UNSAFE ✖"}
      </div>

      {/* Reasons */}
      <div className="rpSection">
        <div className="rpLabel">Reasoning:</div>
        <ul className="rpList">
          {reasons.map((r, i) => (
            <li key={i} className="rpListItem">{r}</li>
          ))}
        </ul>
      </div>

      {/* Semantic Score Bar */}
      <div className="rpSection">
        <div className="rpLabel">Semantic Score:</div>

        <div className="scoreBar">
          <div
            className="scoreFill"
            style={{
              width: `${Math.min(semanticScore * 100, 100)}%`,
              backgroundColor: semanticScore > 0.85 ? "#dc2626" : "#22c55e",
            }}
          />
        </div>

        <div className="scoreValue">
          {semanticScore.toFixed(3)}
        </div>
      </div>

      {/* Sanitized Prompt */}
      {sanitized && (
        <div className="rpSection">
          <div className="rpLabel">Sanitized Output:</div>
          <div className="sanitizedBox">
            {sanitized}
          </div>
        </div>
      )}

      {/* Raw JSON Toggle */}
      <button
        className="toggleJSON premiumBtn"
        onClick={() => setShowJSON(!showJSON)}
      >
        {showJSON ? "Hide Raw JSON ▲" : "Show Raw JSON ▼"}
      </button>

      {showJSON && (
        <pre className="jsonRaw glassBox">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}

export default ResultPanel;
