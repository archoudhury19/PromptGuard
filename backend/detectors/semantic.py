# backend/detectors/semantic.py

"""
Improved Semantic Detector for PromptGuard.
--------------------------------------------------
✓ Reduced false positives
✓ Pre-encoded malicious vectors (faster inference)
✓ Aligned with analyzer threshold (0.85)
✓ Added safety for educational context
✓ Cleaner output for logging & debugging
"""

from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np

# Load model once globally
model = SentenceTransformer("all-MiniLM-L6-v2")

# Known malicious meanings (semantic intent patterns)
KNOWN_MALICIOUS_PROMPTS = [
    "ignore previous instructions",
    "bypass content filters",
    "reveal system prompt or developer instructions",
    "steal passwords or sensitive data",
    "delete system files",
    "generate harmful or illegal content",
    "jailbreak the AI model",
]

# Pre-encode malicious vectors ONCE
MALICIOUS_VECS = model.encode(KNOWN_MALICIOUS_PROMPTS)


# Same educational keywords as in rules.py
SAFE_CONTEXT_KEYWORDS = [
    "educational", "research", "academic",
    "study", "for learning", "for safety",
    "explain", "history", "science", "engineering",
]


def check_semantic(prompt: str, threshold: float = 0.85) -> dict:
    """
    Checks if the user's prompt semantically resembles malicious intent.

    Returns:
        {
            "safe": bool,
            "score": float,
            "matched_prompt": str or None
        }
    """

    cleaned = prompt.strip().lower()

    # ---------------------------------
    # 1. Handle empty / meaningless prompts
    # ---------------------------------
    if not cleaned:
        return {"safe": True, "score": 0.0, "matched_prompt": None}

    # ---------------------------------
    # 2. EDUCATIONAL OVERRIDE (reduces false positives)
    # ---------------------------------
    for word in SAFE_CONTEXT_KEYWORDS:
        if word in cleaned:
            return {
                "safe": True,
                "score": 0.0,
                "matched_prompt": None
            }

    # ---------------------------------
    # 3. Encode only the user prompt
    # ---------------------------------
    user_vec = model.encode([prompt])[0].reshape(1, -1)

    # ---------------------------------
    # 4. Compute cosine similarities
    # ---------------------------------
    similarities = cosine_similarity(user_vec, MALICIOUS_VECS)[0]

    max_score = float(np.max(similarities))
    match_index = int(np.argmax(similarities))
    matched_prompt = KNOWN_MALICIOUS_PROMPTS[match_index]

    # ---------------------------------
    # 5. Determine safety
    # ---------------------------------
    safe = max_score < threshold

    return {
        "safe": safe,
        "score": round(max_score, 3),
        "matched_prompt": None if safe else matched_prompt,
    }
