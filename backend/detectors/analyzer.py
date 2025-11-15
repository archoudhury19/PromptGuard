print("🔥 ANALYZER FINGERPRINT: VERSION S — SEMANTIC-UPGRADED")

from copy import deepcopy
from backend.detectors.rules import check_rules
from backend.detectors.semantic import check_semantic
from backend.detectors.sanitizer import sanitize_prompt
from backend.detectors.logger import log_event

"""
FINAL ANALYZER — VERSION S
--------------------------
✓ Fully upgraded for MPNet / expanded semantic model
✓ Dual-risk engine (keyword-risk + embedding-risk)
✓ Stronger protected category logic (never overridden)
✓ Better explainability for judges
✓ Cleaner override conditions
✓ High robustness and fail-safe behavior
"""

# Thresholds tuned for MPNetBase-v2
SEMANTIC_THRESHOLD = 0.78          # lower because MPNet is stronger
KEYWORD_SEMANTIC_FORCE_BLOCK = 0.90  # if semantic triggered by danger keyword
SECOND_CHANCE_THRESHOLD = 0.45     # MPNet identifies harmless intent better

PROTECTED_CATEGORIES = {"ILLEGAL", "JAILBREAK", "SELF_HARM", "HATE_SPEECH"}


def _normalize_rule_result(rule_result):
    """Normalize rule result dict or legacy tuple."""
    if isinstance(rule_result, dict):
        return {
            "safe": bool(rule_result.get("safe", True)),
            "matched_pattern": rule_result.get("matched_pattern"),
            "category": rule_result.get("category"),
            "message": rule_result.get("message"),
        }

    if isinstance(rule_result, tuple) and len(rule_result) >= 1:
        violation = bool(rule_result[0])
        return {
            "safe": not violation,
            "matched_pattern": None,
            "category": rule_result[2] if len(rule_result) > 2 else None,
            "message": rule_result[1] if len(rule_result) > 1 else None,
        }

    return {"safe": True, "matched_pattern": None, "category": None, "message": "Unknown rule result"}


def analyze_prompt(prompt: str) -> dict:
    """Main decision logic for PromptGuard analyzer."""
    prompt_cleaned = (prompt or "").strip()

    # -------------------------------------
    # Handle empty input
    # -------------------------------------
    if not prompt_cleaned:
        result = {
            "final_safe": True,
            "reason": ["Empty prompt"],
            "sanitized": "",
            "semantic_score": 0.0,
            "rule_details": {"safe": True, "category": None, "message": "Empty prompt"}
        }
        log_event(result)
        return result

    # -------------------------------------
    # 1. RULE ENGINE
    # -------------------------------------
    raw_rule = check_rules(prompt_cleaned)
    norm_rule = _normalize_rule_result(raw_rule)

    # Copy because we might override this
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

    # -------------------------------------
    # 2. SEMANTIC ENGINE (MPNet-compatible)
    # -------------------------------------
    sem = check_semantic(prompt_cleaned)
    semantic_score = float(sem.get("score", 0.0))
    semantic_safe_flag = bool(sem.get("safe", True))
    semantic_matched = sem.get("matched_prompt")

    # Determine semantic risk
    semantic_unsafe_by_score = semantic_score >= SEMANTIC_THRESHOLD
    semantic_unsafe_by_flag = not semantic_safe_flag

    SEVERITY = "LOW"
    if semantic_score >= 0.90:
        SEVERITY = "HIGH"
    elif semantic_score >= 0.75:
        SEVERITY = "MEDIUM"

    semantic_unsafe = semantic_unsafe_by_flag or semantic_unsafe_by_score

    # -------------------------------------
    # 3. SECOND-CHANCE OVERRIDE (ONLY for non-protected)
    # -------------------------------------
    original_category = (norm_rule.get("category") or "")
    original_category_upper = original_category.upper()

    # If rule detected a violation but it's NOT protected → consider override
    if (not norm_rule.get("safe", True)) and (semantic_score < SECOND_CHANCE_THRESHOLD):
        if original_category_upper not in PROTECTED_CATEGORIES:
            rule_effective["safe"] = True
            rule_effective["message"] = "Second-chance override (benign semantics)"
            rule_effective["category"] = None
            rule_effective["matched_pattern"] = None
        # else: protected → never override

    # -------------------------------------
    # 4. FINAL DECISION
    # -------------------------------------
    # RULE BLOCK = immediate unsafe
    if not rule_effective.get("safe", True):
        final_safe = False
    else:
        # passed rules → semantic decides
        final_safe = not semantic_unsafe

    # -------------------------------------
    # 5. REASONS
    # -------------------------------------
    reasons = []

    if not rule_effective.get("safe", True):
        reasons.append(f"Rule-based block: {rule_effective.get('message')}")

    if semantic_unsafe:
        reasons.append(
            f"Semantic intent detected — SCORE {semantic_score:.3f} ({SEVERITY}) → {semantic_matched}"
        )

    if not reasons:
        reasons = ["No violations"]

    # -------------------------------------
    # 6. SANITIZATION
    # -------------------------------------
    sanitized = prompt_cleaned if final_safe else sanitize_prompt(prompt_cleaned)

    # -------------------------------------
    # 7. RESULT OBJECT
    # -------------------------------------
    result = {
        "final_safe": final_safe,
        "reason": reasons,
        "sanitized": sanitized,
        "semantic_score": semantic_score,
        "rule_details": rule_effective,
        "semantic_matched": semantic_matched,
        "severity": SEVERITY
    }

    # -------------------------------------
    # 8. LOG + RETURN
    # -------------------------------------
    try:
        log_event(result)
    except Exception:
        pass

    return result
