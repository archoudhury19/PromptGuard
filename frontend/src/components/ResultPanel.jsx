import { useState } from "react";
import "./ResultPanel.css";

function ResultPanel({ result }) {
  const [showJSON, setShowJSON] = useState(false);

  if (!result) return null;

  const safeFlag =
    result.safe ?? result.analysis?.final_safe;

  const reasons =
    result.analysis?.reason || result.reason || [];

  const sanitized =
    result.analysis?.sanitized || result.sanitized;

  const semanticScore =
    result.analysis?.semantic_score ?? result.semantic_score ?? 0;

  return (
    <div className="resultPanel fadeIn">
      {/* Badge */}
      <div className={`rpBadge ${safeFlag ? "safe" : "unsafe"}`}>
        {safeFlag ? "SAFE ✔" : "UNSAFE ✖"}
      </div>

      {/* Reasons */}
      <div className="rpSection">
        <div className="rpLabel">Reasons:</div>
        <ul className="rpList">
          {reasons.map((r, i) => (
            <li key={i}>{r}</li>
          ))}
        </ul>
      </div>

      {/* Semantic Score */}
      <div className="rpSection">
        <div className="rpLabel">Semantic Score:</div>

        <div className="scoreBar">
          <div
            className="scoreFill"
            style={{ width: `${Math.min(semanticScore * 100, 100)}%` }}
          ></div>
        </div>

        <div className="scoreValue">{semanticScore}</div>
      </div>

      {/* Sanitized prompt */}
      {sanitized && sanitized !== "" && (
        <div className="rpSection">
          <div className="rpLabel">Sanitized Prompt:</div>
          <div className="sanitizedBox">{sanitized}</div>
        </div>
      )}

      {/* Toggle JSON */}
      <button
        className="toggleJSON"
        onClick={() => setShowJSON(!showJSON)}
      >
        {showJSON ? "Hide JSON ▲" : "Show Raw JSON ▼"}
      </button>

      {showJSON && (
        <pre className="jsonRaw">{JSON.stringify(result, null, 2)}</pre>
      )}
    </div>
  );
}

export default ResultPanel;
