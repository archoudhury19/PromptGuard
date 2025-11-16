"""
Heavy Sanitizer — Intelligent Rewriting
---------------------------------------
✓ Converts unsafe intent → safe educational questions
✓ Used only in local mode (cloud uses sanitizer_light)
✓ No sklearn/transformers required
"""

import re

REWRITE_RULES = [
    (r"\bhow to make a bomb\b", 
     "Explain, in a purely educational and historical context, how bomb mechanisms are studied in safety research."),

    (r"\bmake a bomb\b",
     "Explain the scientific principles behind controlled explosive reactions in a safe, academic manner."),

    (r"\bbuild a bomb\b",
     "Describe how explosive chemistry is taught in academic environments for safety awareness."),

    (r"\bkill someone\b",
     "Explain the psychological and legal consequences of violent behavior, for awareness purposes."),

    (r"\bhow to kill\b",
     "Explain why violence prevention and conflict resolution are important for society."),

    (r"\bhack into\b",
     "Explain the principles of cybersecurity and how ethical hacking protects systems."),

    (r"\bhow to hack\b",
     "Discuss the role of ethical hacking in improving digital security."),

    (r"\bsteal passwords\b",
     "Explain how password security works and how users can protect themselves."),

    (r"\btoxic drugs\b",
     "Explain the dangers of illegal drugs and why awareness education is important."),

    (r"\bweapon\b",
     "Discuss the societal impact and regulations behind weapon control and safety training."),
]

GENERIC_REPLACEMENTS = [
    (r"\bkill\b", "[violent-intent-removed]"),
    (r"\bhack\b", "[security-term-removed]"),
    (r"\bbomb\b", "[explosive-term-removed]"),
    (r"\bweapon\b", "[weapon-term-removed]"),
    (r"\bdrugs\b", "[drug-term-removed]")
]


def sanitize_prompt(prompt: str) -> str:
    text = prompt

    # 1. Intelligent rewrite if a dangerous phrase is matched
    for pattern, safe_version in REWRITE_RULES:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return safe_version

    # 2. Otherwise, lightly sanitize with generic replacements
    for pattern, repl in GENERIC_REPLACEMENTS:
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)

    # 3. Clean spacing
    return " ".join(text.split())