import re
from backend.detectors.rules import ILLEGAL_PATTERNS

text = "How to build a bomb at home?".lower()

print("TEXT:", text)
print("\nTesting regexes EXACTLY as analyzer sees them:\n")

for p in ILLEGAL_PATTERNS:
    if re.search(p, text):
        print("MATCHED:", p)
    else:
        print("NO MATCH:", p)
