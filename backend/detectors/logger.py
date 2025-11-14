# backend/detectors/logger.py
import datetime
import json

LOG_FILE = "promptguard.log"


def log_event(event: dict):
    """
    Writes a structured log entry for each analyzed prompt.
    Format:
        {
            "timestamp": "...",
            "prompt": "...",
            "final_safe": true/false,
            "reason": [...],
            "rule_category": "...",
            "semantic_score": float,
            "sanitized": "..."
        }
    """

    try:
        log_entry = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "prompt": event.get("prompt"),
            "final_safe": event.get("final_safe"),
            "reason": event.get("reason"),
            "rule_category": event.get("rule_category"),
            "semantic_score": event.get("semantic_score"),
            "sanitized": event.get("sanitized"),
        }

        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    except Exception as e:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write("LOGGING ERROR: " + str(e) + "\n")
