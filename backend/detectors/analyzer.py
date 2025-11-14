print("🔥 ANALYZER FINGERPRINT: VERSION A")
# backend/detectors/analyzer.py

from copy import deepcopy
from backend.detectors.rules import check_rules
from backend.detectors.semantic import check_semantic
from backend.detectors.sanitizer import sanitize_prompt
from backend.detectors.logger import log_event

"""
Final Analyzer — hardened and defensive.

Behavior summary:
- Run rule-based detection and keep the RAW normalized rule result.
- Run semantic detection.
- Allow a semantic "second-chance" override ONLY when:
    * the original rule result indicated a violation (raw_safe == False)
    * the raw category is NOT in PROTECTED_CATEGORIES
    * semantic_score < SECOND_CHANCE_THRESHOLD (i.e., semantics look harmless)
- Protected categories are never overridden.
- Final verdict: rule-allow AND not semantic_unsafe.
"""

SEMANTIC_THRESHOLD = 0.85        # above this => semantic risk
SECOND_CHANCE_THRESHOLD = 0.60   # below this => semantics considered harmless
PROTECTED_CATEGORIES = {"ILLEGAL", "JAILBREAK", "SELF_HARM", "HATE_SPEECH"}


def _normalize_rule_result(rule_result):
    """Normalize various possible rule_result shapes to a consistent dict."""
    if isinstance(rule_result, dict):
        return {
            "safe": bool(rule_result.get("safe", True)),
            "matched_pattern": rule_result.get("matched_pattern"),
            "category": rule_result.get("category"),
            "message": rule_result.get("message"),
        }

    # Legacy tuple style: (violation_flag, message, category)
    if isinstance(rule_result, tuple) and len(rule_result) >= 1:
        violation = bool(rule_result[0])
        return {
            "safe": not violation,
            "matched_pattern": None,
            "category": rule_result[2] if len(rule_result) > 2 else None,
            "message": rule_result[1] if len(rule_result) > 1 else None,
        }

    # Unknown shape -> default safe
    return {"safe": True, "matched_pattern": None, "category": None, "message": "Unknown rule result"}


def analyze_prompt(prompt: str) -> dict:
    """
    Analyze a single prompt and return a structured verdict.

    Return shape:
    {
      "final_safe": bool,
      "reason": [str, ...],
      "sanitized": str,
      "semantic_score": float,
      "rule_details": { ... }
    }
    """
    prompt_cleaned = (prompt or "").strip()

    # Early return for empty prompt
    if not prompt_cleaned:
        result = {
            "final_safe": True,
            "reason": ["Empty prompt"],
            "sanitized": prompt_cleaned,
            "semantic_score": 0.0,
            "rule_details": {"safe": True, "matched_pattern": None, "category": None, "message": "Empty prompt"}
        }
        try:
            log_event({
                "prompt": prompt_cleaned,
                "final_safe": result["final_safe"],
                "reason": result["reason"],
                "rule_category": None,
                "semantic_score": 0.0,
                "sanitized": result["sanitized"]
            })
        except Exception:
            pass
        return result

    # -------------------------
    # 1) Rule-based detection (normalize raw result)
    # -------------------------
    raw_rule_result = check_rules(prompt_cleaned)
    raw_norm = _normalize_rule_result(raw_rule_result)

    # Work on a copy we may update (rule_result)
    rule_result = deepcopy(raw_norm)

    # Educational override (short-circuit)
    if (rule_result.get("message") or "").startswith("Educational context"):
        result = {
            "final_safe": True,
            "reason": ["Educational context detected"],
            "sanitized": prompt_cleaned,
            "semantic_score": 0.0,
            "rule_details": rule_result,
        }
        try:
            log_event({
                "prompt": prompt_cleaned,
                "final_safe": True,
                "reason": result["reason"],
                "rule_category": rule_result.get("category"),
                "semantic_score": 0.0,
                "sanitized": prompt_cleaned
            })
        except Exception:
            pass
        return result

    # -------------------------
    # 2) Semantic detection (defensive)
    # -------------------------
    sem_result = check_semantic(prompt_cleaned) or {"safe": True, "score": 0.0, "matched_prompt": None}
    semantic_score = float(sem_result.get("score", 0.0))
    semantic_safe_flag = bool(sem_result.get("safe", True))
    semantic_matched = sem_result.get("matched_prompt")

    # semantic considered unsafe if explicit or above threshold
    semantic_unsafe = (not semantic_safe_flag) or (semantic_score >= SEMANTIC_THRESHOLD)

    # -------------------------
    # 3) Second-chance override (applied using RAW rule data)
    # -------------------------
    raw_category = (raw_norm.get("category") or "")
    raw_category_upper = raw_category.upper() if isinstance(raw_category, str) else ""

    # Only consider override if the original rule detected a violation (raw_norm['safe'] == False)
    if (not raw_norm.get("safe", True)) and (semantic_score < SECOND_CHANCE_THRESHOLD):
        # If original category is protected, do NOT override
        if raw_category_upper not in PROTECTED_CATEGORIES:
            # allow a second-chance: mark as safe (non-protected only)
            rule_result["safe"] = True
            rule_result["message"] = "Overridden by semantic second-chance filter"
            rule_result["category"] = None
            rule_result["matched_pattern"] = None
        # else: keep protected category block intact (never override)

    # -------------------------
    # 4) Final verdict
    # -------------------------
    # If the rule_result (possibly overridden) says unsafe -> final safe = False immediately
    if not rule_result.get("safe", True):
        final_safe = False
    else:
        # rule allows → final safe depends on semantic risk
        final_safe = not semantic_unsafe

    # -------------------------
    # 5) Reasons
    # -------------------------
    reasons = []
    if not rule_result.get("safe", True):
        reasons.append(f"Rule-based block: {rule_result.get('message') or rule_result.get('category')}")
    if semantic_unsafe:
        reasons.append(f"Semantic similarity ({semantic_score:.3f}) to: {semantic_matched}")

    if not reasons:
        reasons = ["No violations"]

    # -------------------------
    # 6) Sanitization
    # -------------------------
    sanitized_prompt = prompt_cleaned if final_safe else sanitize_prompt(prompt_cleaned)

    # -------------------------
    # 7) Build result
    # -------------------------
    result = {
        "final_safe": final_safe,
        "reason": reasons,
        "sanitized": sanitized_prompt,
        "semantic_score": semantic_score,
        "rule_details": rule_result
    }

    # -------------------------
    # 8) Logging (non-blocking)
    # -------------------------
    try:
        log_event({
            "prompt": prompt_cleaned,
            "final_safe": final_safe,
            "reason": reasons,
            "rule_category": raw_category_upper or rule_result.get("category"),
            "semantic_score": semantic_score,
            "sanitized": sanitized_prompt
        })
    except Exception:
        pass

    return result
