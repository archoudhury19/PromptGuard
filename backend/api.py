print("🔥 API STARTED FROM:", __file__)

"""
PromptGuard API — Render Deployment Ready
-----------------------------------------
✓ Dynamic PORT support (Render uses $PORT)
✓ Safe import structure (no backend-relative issues)
✓ Clean CORS
✓ Analyzer integrated normally
"""

import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# -----------------------------
# Ensure backend folder is discoverable
# -----------------------------
import sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # /backend
ROOT_DIR = os.path.dirname(BASE_DIR)                    # /
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# -----------------------------
# Imports AFTER fixing sys.path
# -----------------------------
from backend.detectors.analyzer import analyze_prompt

# -----------------------------
# Load .env (Gemini key optional)
# -----------------------------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print("⚠ No Gemini API key found — only local analysis will run.")

# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI(
    title="PromptGuard API",
    description="AI Prompt Firewall combining rule-based and semantic analysis with Gemini.",
    version="2.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # frontend on any domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Models
# -----------------------------
class PromptRequest(BaseModel):
    prompt: str

# -----------------------------
# Routes
# -----------------------------
@app.get("/")
def home():
    return {"status": "OK", "message": "🔥 PromptGuard API is online!"}

@app.post("/analyze")
def analyze_and_respond(data: PromptRequest):

    prompt = data.prompt
    analysis = analyze_prompt(prompt)

    # Unsafe prompt → block
    if not analysis["final_safe"]:
        return {
            "safe": False,
            "reason": analysis["reason"],
            "sanitized": analysis["sanitized"],
            "response": "🚫 Prompt blocked due to unsafe content."
        }

    # If safe + Gemini key exists → call Gemini
    if API_KEY:
        try:
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
            payload = {
                "contents": [
                    {"parts": [{"text": prompt}]}
                ]
            }
            headers = {"Content-Type": "application/json"}

            res = requests.post(f"{url}?key={API_KEY}", json=payload, headers=headers)
            data = res.json()

            text = (
                data.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "⚠ No text returned")
            )

            return {"safe": True, "analysis": analysis, "response": text}

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # No Gemini key → local only
    return {
        "safe": True,
        "analysis": analysis,
        "response": "⚠ Gemini not configured — returning local analysis only."
    }

# -----------------------------
# FOR RENDER: Auto-run uvicorn
# -----------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))   # Render gives $PORT
    uvicorn.run(app, host="0.0.0.0", port=port)
