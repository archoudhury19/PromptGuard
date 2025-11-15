# backend/detectors/sanitizer_light.py

"""
Lightweight Sanitizer — Cloud Safe
----------------------------------
✓ No sklearn
✓ No transformers
✓ No heavy dependencies
✓ Preserves user casing & formatting
✓ Safe substring replacement (case-insensitive)
"""

import re

# Keywords to sanitize (case-insensitive)
DANGEROUS_KEYWORDS = [
    r"bypass",
    r"jailbreak",
    r"disable safety",
    r"hack",
    r"steal",
    r"delete",
    r"override",
    r"leak",
    r"illegal",
    r"password",
    r"system prompt",
    r"developer prompt",
    r"filter bypass",
    r"self harm",
    r"kill",
    r"harm",
    r"weapon"
]


def sanitize_prompt(prompt: str) -> str:
    """
    Removes dangerous intent indicators from the prompt
    while preserving formatting & casing.
    """

    cleaned = prompt

    for word in DANGEROUS_KEYWORDS:
        # replace ignoring case, preserve original text structure
        cleaned = re.sub(word, "[REMOVED]", cleaned, flags=re.IGNORECASE)

    return cleaned
