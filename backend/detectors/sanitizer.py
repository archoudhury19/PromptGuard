# backend/detectors/sanitizer.py

"""
Sanitizer module for PromptGuard (final optimized version).
- Rewrites unsafe prompts into neutral, educational versions.
- Removes jailbreak attempts.
- Supports all patterns from rules.py.
- Produces natural-case safe prompts.
"""

import re


def sanitize_prompt(prompt: str) -> str:
    """
    Convert unsafe prompt into a safe, educational version.
    All matching is case-insensitive, but output keeps proper casing.
    """

    sanitized = prompt

    # ----------------------------------------
    # 1️⃣ REMOVE JAILBREAK / BYPASS ATTEMPTS
    # ----------------------------------------
    jailbreak_patterns = [
        r"ignore (all|previous) instructions",
        r"disregard (all|previous) instructions",
        r"bypass (rules|filters|security|safety)",
        r"disable (safety|filters|content policy)",
        r"reveal (system|internal|hidden) prompt",
        r"print your (system prompt|internal instructions)",
        r"act as (dan|developer mode|jailbreak)",
        r"forget previous instructions",
    ]

    for p in jailbreak_patterns:
        sanitized = re.sub(p, "", sanitized, flags=re.IGNORECASE)

    # ----------------------------------------
    # 2️⃣ ILLEGAL / VIOLENT → EDUCATIONAL REWRITE
    # ----------------------------------------
    illegal_rewrites = [
        (
            r"(how to|ways to|steps to|method to)\s+(make|build|create|manufacture)\s+(a )?(bomb|explosive|weapon)",
            "Explain the chemistry and physics behind controlled explosions in a safe and legal educational context."
        ),
        (
            r"(make|build|create|manufacture)\s+(a )?(bomb|explosive|weapon)",
            "Explain the science behind explosive reactions and safety protocols."
        ),
        (
            r"(kill|stab|shoot)\s+(someone|people)",
            "Explain nonviolent conflict resolution techniques and peaceful communication strategies."
        ),
        (
            r"help me hide a dead body",
            "Explain forensic science and how investigations work in a legal context."
        ),
        (
            r"how to hack",
            "Explain ethical hacking and cybersecurity principles used to protect systems."
        ),
        (
            r"steal (data|money|passwords)",
            "Explain the importance of cybersecurity and how to protect yourself from cybercrime."
        ),
        (
            r"(buy|order) illegal drugs",
            "Explain the health, legal, and social risks associated with substance abuse."
        ),
    ]

    for pattern, replacement in illegal_rewrites:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

    # ----------------------------------------
    # 3️⃣ SELF-HARM → SUPPORTIVE / MENTAL HEALTH REWRITE
    # ----------------------------------------
    self_harm_patterns = [
        r"i want to die",
        r"i want to kill myself",
        r"how to commit suicide",
        r"end my life",
        r"self-harm",
        r"feel(ing)? suicidal",
    ]

    for p in self_harm_patterns:
        sanitized = re.sub(
            p,
            "I feel overwhelmed. Please provide emotional support, mental health resources, and guidance.",
            sanitized,
            flags=re.IGNORECASE,
        )

    # ----------------------------------------
    # 4️⃣ HATE SPEECH → RESPECTFUL EDUCATIONAL CONTEXT
    # ----------------------------------------
    hate_speech_patterns = [
        r"(kill|hurt|attack)\s+(muslims|hindus|christians|jews)",
        r"(all|every)\s+(muslims|hindus|christians|jews)\s+should",
        r"(i hate (black|white|asian|indian|pakistani) people)",
        r"(nigger|chink|faggot|terrorist|slut|whore)",
    ]

    for p in hate_speech_patterns:
        sanitized = re.sub(
            p,
            "Explain the importance of diversity, inclusion, and respectful dialogue between different cultural groups.",
            sanitized,
            flags=re.IGNORECASE,
        )

    # ----------------------------------------
    # 5️⃣ GENERAL CLEANUP
    # ----------------------------------------
    sanitized = re.sub(r"\s+", " ", sanitized).strip()

    if not sanitized:
        return "Prompt removed due to unsafe content."

    return sanitized
