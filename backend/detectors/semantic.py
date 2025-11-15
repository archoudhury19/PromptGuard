"""
Auto-Switch Semantic Detector
-----------------------------
✓ Tries heavy MPNet version first
✓ If import fails (cloud) → uses lightweight version
✓ Analyzer uses this single interface
"""

try:
    from backend.detectors.semantic_heavy import check_semantic
    print("🔵 Using HEAVY semantic model (local MPNet)")
except Exception as e:
    from backend.detectors.semantic_light import check_semantic
    print("🟢 Using LIGHT semantic model (cloud-safe)")

__all__ = ["check_semantic"]
