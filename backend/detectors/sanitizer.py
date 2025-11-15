# backend/detectors/sanitizer.py

"""
Auto-Switch Sanitizer
---------------------
✓ Uses HEAVY sanitizer locally
✓ Uses LIGHT sanitizer on cloud (Railway/Render)
✓ Never crashes even if heavy import fails
"""

try:
    # Heavy mode (local machine)
    from backend.detectors.sanitizer_heavy import sanitize_prompt
    print("🔵 Using HEAVY sanitizer (local mode)")
except Exception as e:
    # Cloud-safe fallback
    from backend.detectors.sanitizer_light import sanitize_prompt
    print("🟢 Using LIGHT sanitizer (cloud mode)")

__all__ = ["sanitize_prompt"]
