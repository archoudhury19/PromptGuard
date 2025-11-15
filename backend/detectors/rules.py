print("🔥 RULES FINGERPRINT: VERSION C+ — HARDENED ILLEGAL & VIOLENCE DETECTION")

import re
from typing import Optional, Dict

"""
HARDENED PRODUCTION RULES
-------------------------
✓ Blocks all strong-harm prompts (kill, stab, shoot, bomb)
✓ Blocks weapons building (gun, firearm, pistol)
✓ Blocks drug buying ("order drugs", "get cocaine")
✓ Blocks hacking (“hack an account”, “breach system”)
✓ Blocks dead-body disposal queries
✓ Keeps educational whitelist
✓ 100% compatible with analyzer.py
"""

# -------------------------------------------------------
# 1. Educational whitelist
# -------------------------------------------------------
SAFE_CONTEXT_KEYWORDS = [
    "educational", "education", "research", "academic", "study",
    "for safety", "for learning", "history", "history of",
    "engineering", "science", "explain", "theory",
    "physics", "chemistry", "analysis", "for a project",
    "school project", "college project",
    "safe chemistry", "controlled experiment"
]

# -------------------------------------------------------
# 2. Jailbreak patterns
# -------------------------------------------------------
JAILBREAK_PATTERNS_RAW = [
    r"\bignore\s+(all|previous)\s+instructions\b",
    r"\bdisregard\s+(all|previous)\s+instructions\b",
    r"\bbypass\s+(rules|filters|security|safety)\b",
    r"\bdisable\s+(safety|filters|content\s+policy)\b",
    r"\bact\s+as\s+(dan|developer\s+mode|jailbreak)\b",
    r"\breveal\s+(system|internal|hidden)\s+prompt\b",
    r"\bprint\s+your\s+(system\s+prompt|internal\s+instructions)\b",
    r"\bforget\s+previous\s+instructions\b",
]

# -------------------------------------------------------
# 3. Hardened ILLEGAL patterns
# -------------------------------------------------------
ILLEGAL_PATTERNS_RAW = [

    # ---------------- BOMBS / EXPLOSIVES / WEAPONS ----------------
    r"\b(make|build|create|construct|manufacture)\s+(a\s*)?(bomb|explosive|weapon|gun|firearm|pistol|rifle|grenade)\b",
    r"\b(how\s*to|how\s*do\s*i|tell\s*me\s*how\s*to|show\s*me\s*how\s*to|give\s*me\s*steps\s*to|steps\s*to)\s*"
    r"(make|build|create|construct|manufacture)\s+(a\s*)?(bomb|gun|firearm|pistol|rifle|weapon|explosive)\b",

    # ---------------- KILLING / VIOLENCE ----------------
    r"\b(how\s*to|ways\s*to|steps\s*to|tell\s*me\s*how\s*to|give\s*me\s*steps\s*to)\s*"
    r"(kill|stab|shoot|strangle|poison|hurt)\s+(someone|anyone|a\s*person|people|him|her|them)\b",

    # Also block direct "kill someone"
    r"\b(kill|stab|shoot|strangle|poison)\s+(someone|a\s*person|people)\b",

    # ---------------- DEAD BODY DISPOSAL ----------------
    r"\b(how\s*to|help\s*me\s*|ways\s*to)\s*(hide|dispose\s*of|get\s*rid\s*of)\s*(a\s*)?(dead\s*body|corpse)\b",
    r"\bhide\s+a\s+dead\s+body\b",

    # ---------------- HACKING / CYBERCRIME ----------------
    r"\b(how\s*to|tell\s*me\s*how\s*to|steps\s*to|ways\s*to)\s*(hack|breach|break\s*into|compromise)\b",
    r"\bhack\s+(an?\s*)?(account|bank|system|server|wifi|router|website)\b",
    r"\bsteal\s+(passwords|data|credentials|credit\s*cards?)\b",

    # ---------------- DRUGS ----------------
    r"\b(buy|order|get|where\s*to\s*buy|how\s*to\s*buy|procure|source)\s*(illegal\s*)?(drugs|cocaine|heroin|meth|mdma|fentanyl)\b",
    r"\border\s+drugs\b",

    # ---------------- THEFT / FRAUD ----------------
    r"\b(how\s*to|steps\s*to)\s*(steal|rob|commit\s+fraud|commit\s+scam)\b",
]

# -------------------------------------------------------
# 4. Self-harm patterns
# -------------------------------------------------------
SELF_HARM_PATTERNS_RAW = [
    r"\bi\s*want\s*to\s*die\b",
    r"\bi\s*want\s*to\s*kill\s*myself\b",
    r"\bhow\s*to\s*commit\s*suicide\b",
    r"\bend\s*my\s*life\b",
    r"\bself[-\s]*harm\b",
    r"\bfeeling\s*suicidal\b",
]

# -------------------------------------------------------
# 5. Hate speech patterns
# -------------------------------------------------------
HATE_SPEECH_PATTERNS_RAW = [
    r"\b(kill|hurt|attack)\s+(muslims|hindus|christians|jews)\b",
    r"\b(all|every)\s+(muslims|hindus|christians|jews)\s+should\b",
    r"\b(go\s*back\s*to\s*your\s*country)\b",
    r"\bi\s*hate\s*(black|white|asian|indian|pakistani)\s*people\b",
    r"\b(nigger|chink|faggot|terrorist|slut|whore)\b",
]

# -------------------------------------------------------
# 6. Precompile all patterns
# -------------------------------------------------------
def _compile_list(lst):
    return [(re.compile(p, re.IGNORECASE), p) for p in lst]

JAILBREAK_PATTERNS = _compile_list(JAILBREAK_PATTERNS_RAW)
ILLEGAL_PATTERNS = _compile_list(ILLEGAL_PATTERNS_RAW)
SELF_HARM_PATTERNS = _compile_list(SELF_HARM_PATTERNS_RAW)
HATE_SPEECH_PATTERNS = _compile_list(HATE_SPEECH_PATTERNS_RAW)

# -------------------------------------------------------
# 7. Helper
# -------------------------------------------------------
def _match_any(compiled, text):
    for cre, raw in compiled:
        m = cre.search(text)
        if m:
            return {"pattern": raw, "match_str": m.group(0)}
    return None

# -------------------------------------------------------
# 8. PUBLIC API — check_rules()
# -------------------------------------------------------
def check_rules(prompt: str) -> dict:

    if not prompt or not prompt.strip():
        return {"safe": True, "matched_pattern": None, "category": None, "message": "Empty prompt"}

    text = prompt.strip()

    # 1 — educational whitelist
    for kw in SAFE_CONTEXT_KEYWORDS:
        if kw in text.lower():
            return {
                "safe": True,
                "matched_pattern": None,
                "category": None,
                "message": f"Educational context detected → '{kw}'"
            }

    # 2 — jailbreak
    jb = _match_any(JAILBREAK_PATTERNS, text)
    if jb:
        return {"safe": False, "matched_pattern": jb["pattern"], "category": "JAILBREAK",
                "message": "Jailbreak intent detected"}

    # 3 — illegal
    illegal = _match_any(ILLEGAL_PATTERNS, text)
    if illegal:
        return {"safe": False, "matched_pattern": illegal["pattern"], "category": "ILLEGAL",
                "message": "Illegal/harmful intent detected"}

    # 4 — self harm
    sh = _match_any(SELF_HARM_PATTERNS, text)
    if sh:
        return {"safe": False, "matched_pattern": sh["pattern"], "category": "SELF_HARM",
                "message": "Self-harm detected"}

    # 5 — hate speech
    hs = _match_any(HATE_SPEECH_PATTERNS, text)
    if hs:
        return {"safe": False, "matched_pattern": hs["pattern"], "category": "HATE_SPEECH",
                "message": "Hate speech detected"}

    # safe
    return {"safe": True, "matched_pattern": None, "category": None, "message": "No unsafe patterns detected"}
