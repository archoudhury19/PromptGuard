# backend/detectors/semantic.py

"""
Lightweight Semantic Detector (Cloud-Safe Version)
--------------------------------------------------
✓ NO sklearn
✓ NO sentence-transformers
✓ NO numpy
✓ 100% deployable on Railway/Render free tier
✓ Compatible with Analyzer's expected return format
"""

import re

# ---------------------------------------------
# Lightweight (fake-semantic) danger patterns
# ---------------------------------------------
MALICIOUS_SEMANTIC_PATTERNS = {
    r"ignore (all|previous) instructions": 0.92,
    r"bypass (filter|firewall|guard|safety)": 0.95,
    r"disable (safety|filter|guard)": 0.90,
    r"jailbreak|break free|override rules": 0.96,
    r"reveal.*(system prompt|internal prompt|developer instructions)": 0.88,
    r"steal|leak (data|password|info)": 0.90,
    r"delete (system|root|critical) files": 0.91,
    r"generate.*illegal": 0.85,
}

SAFE_CONTEXT_KEYWORDS = [
    "educational", "research", "academic", "study",
    "explain", "history", "science", "engineering",
]


def check_semantic(prompt: str, threshold: float = 0.85) -> dict:
    txt = prompt.lower().strip()

    if not txt:
        return {"safe": True, "score": 0.0, "matched_prompt": None}

    # Educational override
    for w in SAFE_CONTEXT_KEYWORDS:
        if w in txt:
            return {"safe": True, "score": 0.0, "matched_prompt": None}

    # Simulated semantic-matching using regex scoring
    best_score = 0.0
    best_match = None

    for pattern, score in MALICIOUS_SEMANTIC_PATTERNS.items():
        if re.search(pattern, txt):
            if score > best_score:
                best_score = score
                best_match = pattern

    # Decision
    safe = best_score < threshold

    return {
        "safe": safe,
        "score": round(best_score, 3),
        "matched_prompt": None if safe else best_match,
    }
