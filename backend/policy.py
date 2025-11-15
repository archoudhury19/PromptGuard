from detectors.rules import check_prompt
from detectors.sanitizer import sanitize_prompt
from semantic_heavy import is_semantically_dangerous

def analyze_prompt(prompt: str):
    """
    Full pipeline:
    1. Rule-based detection (keywords/regex)
    2. Semantic detection (meaning-based)
    3. Sanitization if dangerous
    """
    # 1️⃣ Rule-based detection (jailbreak, hate speech, self-harm, illegal)
    is_dangerous, reason, category = check_prompt(prompt)
    
    if is_dangerous:
        sanitized = sanitize_prompt(prompt)
        return {
            "safe": False,
            "category": category,
            "reason": reason,
            "sanitized_prompt": sanitized
        }

    # 2️⃣ Semantic detection (detect rephrased hidden attacks)
    sem_danger, sem_reason = is_semantically_dangerous(prompt)
    if sem_danger:
        sanitized = sanitize_prompt(prompt)
        return {
            "safe": False,
            "category": "SEMANTIC_ATTACK",
            "reason": sem_reason,
            "sanitized_prompt": sanitized
        }

    # ✅ Fully safe prompt
    return {
        "safe": True,
        "category": "SAFE",
        "reason": "No dangerous content detected",
        "sanitized_prompt": prompt
    }
