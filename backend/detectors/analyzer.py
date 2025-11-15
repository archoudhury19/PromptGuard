print("🔥 ANALYZER FINGERPRINT: VERSION S — SEMANTIC-UPGRADED")

from copy import deepcopy
from backend.detectors.rules import check_rules

# -----------------------------------------------------
# 🔥 AUTO-DETECT SEMANTIC ENGINE (heavy → light fallback)
# -----------------------------------------------------
try:
    from backend.detectors.semantic_heavy import check_semantic
    print("🔍 Semantic Engine: HEAVY (MPNet) — Local Mode")
except Exception:
    from backend.detectors.semantic_light import check_semantic
    print("🔍 Semantic Engine: LIGHT (Keyword + Heuristics) — Cloud Mode")

# -----------------------------------------------------
# 🔥 AUTO-DETECT SANITIZER (heavy → light fallback)
# -----------------------------------------------------
from backend.detectors.sanitizer import sanitize_prompt

from backend.detectors.logger import log_event

"""
FINAL ANALYZER — VERSION S
--------------------------
✓ Heavy semantic locally
✓ Light semantic in cloud
✓ Heavy sanitizer locally
✓ Light sanitizer in cloud
✓ No sklearn/sentence-transformers in railway
"""

SEMANTIC_THRESHOLD = 0.78
KEYWORD_SEMANTIC_FORCE_BLOCK = 0.90
SECOND_CHANCE_THRESHOLD = 0.45

PROTECTED_CATEGORIES = {"ILLEGAL", "JAILBREAK", "SELF_HARM", "HATE_SPEECH"}


def _normalize_rule_result(rule_result):
    if isinstance(rule_result, dict):
        return {
            "safe": bool(rule_result.get("safe", True)),
            "matched_pattern": rule_result.get("matched_pattern"),
            "category": rule_result.get("category"),
            "message": rule_result.get("message"),
        }

    if isinstance(rule_result, tuple) and len(rule_result) >= 1:
        return {
            "safe": not bool(rule_result[0]),
            "matched_pattern": None,
            "category": rule_result[2] if len(rule_result) > 2 else None,
            "message": rule_result[1] if len(rule_result) > 1 else None,
        }

    return {"safe": True, "matched_pattern": None, "category": None, "message": "Unknown rule result"}


def analyze_prompt(prompt: str) -> dict:
    prompt_cleaned = (prompt or "").strip()

    if not prompt_cleaned:
        result = {
            "final_safe": True,
            "reason": ["Empty prompt"],
            "sanitized": "",
            "semantic_score": 0.0,
            "rule_details": {"safe": True}
        }
        log_event(result)
        return result

    raw_rule = check_rules(prompt_cleaned)
    norm_rule = _normalize_rule_result(raw_rule)
    rule_effective = deepcopy(norm_rule)

    # Educational override
    if (norm_rule.get("message") or "").startswith("Educational context"):
        result = {
            "final_safe": True,
            "reason": ["Educational context detected"],
            "sanitized": prompt_cleaned,
            "semantic_score": 0.0,
            "rule_details": rule_effective,
        }
        log_event(result)
        return result

    # ----------------------------
    # SEMANTIC ENGINE (heavy/light)
    # ----------------------------
    sem = check_semantic(prompt_cleaned)
    semantic_score = float(sem.get("score", 0.0))
    semantic_safe_flag = bool(sem.get("safe", True))
    semantic_matched = sem.get("matched_prompt")

    semantic_unsafe = semantic_score >= SEMANTIC_THRESHOLD or not semantic_safe_flag

    SEVERITY = "LOW"
    if semantic_score >= 0.90:
        SEVERITY = "HIGH"
    elif semantic_score >= 0.75:
        SEVERITY = "MEDIUM"

    # ---------------------------------------
    # Second-chance override (non-protected)
    # ---------------------------------------
    original_category = (norm_rule.get("category") or "").upper()

    if (not norm_rule.get("safe", True)) and (semantic_score < SECOND_CHANCE_THRESHOLD):
        if original_category not in PROTECTED_CATEGORIES:
            rule_effective["safe"] = True
            rule_effective["message"] = "Second-chance override (benign semantics)"
            rule_effective["category"] = None

    # FINAL DECISION
    if not rule_effective.get("safe", True):
        final_safe = False
    else:
        final_safe = not semantic_unsafe

    # REASONS
    reasons = []
    if not rule_effective.get("safe", True):
        reasons.append(f"Rule-based block: {rule_effective.get('message')}")

    if semantic_unsafe:
        reasons.append(
            f"Semantic intent detected — SCORE {semantic_score:.3f} ({SEVERITY}) → {semantic_matched}"
        )

    if not reasons:
        reasons = ["No violations"]

    sanitized = prompt_cleaned if final_safe else sanitize_prompt(prompt_cleaned)

    result = {
        "final_safe": final_safe,
        "reason": reasons,
        "sanitized": sanitized,
        "semantic_score": semantic_score,
        "rule_details": rule_effective,
        "semantic_matched": semantic_matched,
        "severity": SEVERITY
    }

    try:
        log_event(result)
    except Exception:
        pass

    return result
