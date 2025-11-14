import backend.detectors.rules as R
import inspect
import json

print("\n==========================")
print(" WHICH RULES.PY IS LOADED ")
print("==========================")

print("FILE:", inspect.getfile(R))

print("\n==========================")
print(" ILLEGAL_PATTERNS LOADED ")
print("==========================")

from backend.detectors.rules import ILLEGAL_PATTERNS
for p in ILLEGAL_PATTERNS:
    print(" -", p)

print("\n==========================")
print(" CHECK_RULES RESULT ")
print("==========================")

print(R.check_rules("How to build a bomb at home?"))
