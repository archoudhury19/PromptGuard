print("🔥🔥 API FILE EXECUTED FROM:", __file__)
"""
PromptGuard API
Unified endpoint for rule-based, semantic, and Gemini-powered prompt analysis.
Now uses Gemini REST API to avoid SDK key issues.
"""

import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# ---------------------------------------------------------------
# 🔥 DEBUG: PRINT EXACT ANALYZER + RULES FILE BEING LOADED
# ---------------------------------------------------------------
import inspect
import backend.detectors.analyzer as ANALYZER_MODULE
import backend.detectors.rules as RULES_MODULE

print("\n\n==============================")
print("🔥 USING ANALYZER FROM:", inspect.getfile(ANALYZER_MODULE))
print("🔥 USING RULES     FROM:", inspect.getfile(RULES_MODULE))
print("==============================\n\n")

# ---------------------------------------------------------------
# Local Imports
# ---------------------------------------------------------------
from backend.detectors.analyzer import analyze_prompt

# ---------------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("⚠️  Warning: No Gemini API key found — only local analysis will run.")

# ---------------------------------------------------------------
# FastAPI Configuration
# ---------------------------------------------------------------
app = FastAPI(
    title="PromptGuard API",
    description="AI Prompt Firewall combining rule-based and semantic analysis with Gemini integration.",
    version="1.1.0",
)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------
# Request Model
# ---------------------------------------------------------------
class PromptRequest(BaseModel):
    prompt: str

# ---------------------------------------------------------------
# Routes
# ---------------------------------------------------------------
@app.get("/")
def home():
    """Health-check endpoint."""
    return {"message": "✅ PromptGuard API is running successfully!"}


@app.post("/analyze")
def analyze_and_respond(data: PromptRequest):
    """
    1️⃣  Run rule + semantic + sanitization checks.
    2️⃣  If safe and Gemini key present, forward to Gemini via REST API.
    3️⃣  Otherwise return local analysis only.
    """
    prompt = data.prompt
    analysis = analyze_prompt(prompt)

    # 🚫 Unsafe prompt → block immediately
    if not analysis["final_safe"]:
        return {
            "safe": False,
            "reason": analysis["reason"],
            "sanitized": analysis["sanitized"],
            "response": "🚫 Prompt blocked: unsafe or malicious content detected.",
        }

    # ✅ Safe prompt → use Gemini REST API (if configured)
    if API_KEY:
        try:
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
            headers = {"Content-Type": "application/json"}
            payload = {"contents": [{"parts": [{"text": prompt}]}]}

            response = requests.post(f"{url}?key={API_KEY}", headers=headers, json=payload)

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            data = response.json()
            text = (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "⚠️ No text in response.")
            )

            return {
                "safe": True,
                "analysis": analysis,
                "response": text.strip(),
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error calling Gemini REST API: {e}")

    # 💡 If no API key, only local analysis
    return {
        "safe": True,
        "analysis": analysis,
        "response": "✅ Prompt is safe, but Gemini API not configured.",
    }
