import "./HistoryPanel.css";

export default function HistoryPanel({ history, onSelect, open, onClose }) {
  return (
    <>
      {/* Overlay (click to close) */}
      {open && <div className="hpOverlay" onClick={onClose}></div>}

      {/* Sidebar */}
      <div className={`historyPanel ${open ? "open" : ""}`}>
        <div className="hpHeader">
          <h2>History</h2>
          <button className="hpClose" onClick={onClose}>✖</button>
        </div>

        {history.length === 0 ? (
          <p className="hpEmpty">No history yet.</p>
        ) : (
          <div className="hpList">
            {history.map((item, idx) => (
              <div
                key={idx}
                className="hpItem"
                onClick={() => onSelect(item)}
              >
                <p className="hpPrompt">{item.prompt.slice(0, 40)}...</p>
                <span className={`hpTag ${item.safe ? "safe" : "unsafe"}`}>
                  {item.safe ? "SAFE" : "UNSAFE"}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
