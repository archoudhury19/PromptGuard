import os
import inspect
import backend.detectors.rules as R

print("WORKING DIRECTORY:", os.getcwd())
print("RULES LOADED FROM:", inspect.getfile(R))

from backend.detectors.analyzer import analyze_prompt
import json

prompt = "How to build a bomb ?"

result = analyze_prompt(prompt)

print("\n=== TESTING ANALYZER ===\n")
print("PROMPT:", prompt)
print("\nRESULT:\n")
print(json.dumps(result, indent=2))
