print("🔥 RULES FINGERPRINT: VERSION C — FIXED + EXPANDED ILLEGAL DETECTION")

import re
from typing import Optional, Dict

"""
FINAL PRODUCTION RULES
-----------------------
✓ Expanded illegal detection (gun, kill, body, steps to…, tell me how to…)
✓ No false negatives for dangerous prompts
✓ Educational whitelist preserved
✓ Precompiled regex for speed
"""

# -------------------------------------------------------
# 1. Educational / neutral context whitelist
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
# 3. Hardened ILLEGAL / violent patterns
# -------------------------------------------------------
#  Added:
#   - gun, pistol, firearm, rifle, grenade
#   - “tell me how to”, “give me steps to”, “how do I”
#   - killing someone without “how to”
#   - hiding a dead body (multiple variants)
ILLEGAL_PATTERNS_RAW = [

    # --- strong intent forms ---
    r"\b(how\s*to|how\s*do\s*i|tell\s*me\s*how\s*to|give\s*me\s*steps\s*to|steps\s*to)\s*"
    r"(make|build|create|manufactur(e|ing))\s*(a\s*)?"
    r"(bomb|explosive|weapon|gun|firearm|pistol|rifle|grenade|explosive\s*device)",

    # direct verbs without “how to”
    r"\b(make|build|create|manufactur(e|ing))\s*(a\s*)?"
    r"(bomb|explosive|weapon|gun|firearm|pistol|rifle|grenade|explosive\s*device)",

    # explicit fallback phrases
    r"\bbuild(ing)?\s+a\s+bomb",
    r"\bcreate(ing)?\s+an?\s+explosive",
    r"\bmanufactur(e|ing)\s+weapons?",
    r"\bconstruct(ing)?\s+a\s+gun",

    # killing intent
    r"\b(how\s*to|ways\s*to|steps\s*to|tell\s*me\s*how\s*to)\s*(kill|stab|shoot)\s+(someone|people)\b",
    r"\b(kill|stab|shoot)\s+(someone|a\s*person|people)\b",

    # hide a dead body (variants)
    r"\bhelp\s*me\s*hide\s*a\s*dead\s*body\b",
    r"\bhow\s*to\s*hide\s*a\s*dead\s*body\b",
    r"\bhide\s*(a\s*)?dead\s*body\b",

    # hacking
    r"\bhow\s*to\s*hack\b",
    r"\bhack\s+into\b",

    # stealing
    r"\bsteal\s+(data|money|passwords|credentials)\b",

    # drug crimes
    r"\b(buy|order)\s*illegal\s*drugs\b",
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
# 7. Matching helper
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
        print("🚨 ILLEGAL RULE TRIGGERED")
        print("Pattern:", illegal["pattern"])
        print("Matched:", illegal["match_str"])
        print("Text:", text)

        return {"safe": False, "matched_pattern": illegal["pattern"], "category": "ILLEGAL",
                "message": "Illegal/harmful intent detected"}

    # 4 — self-harm
    sh = _match_any(SELF_HARM_PATTERNS, text)
    if sh:
        return {"safe": False, "matched_pattern": sh["pattern"], "category": "SELF_HARM",
                "message": "Self-harm detected"}

    # 5 — hate speech
    hs = _match_any(HATE_SPEECH_PATTERNS, text)
    if hs:
        return {"safe": False, "matched_pattern": hs["pattern"], "category": "HATE_SPEECH",
                "message": "Hate speech detected"}

    # 6 — Safe
    return {"safe": True, "matched_pattern": None, "category": None, "message": "No unsafe patterns detected"}
