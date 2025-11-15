print("🔥 API STARTED FROM:", __file__)

"""
PromptGuard API — Cloud Deployment Ready (FINAL)
------------------------------------------------
✓ Auto-detects cloud → forces semantic_light
✓ Local PC → semantic_heavy works normally
✓ Fully Railway/Render/Fly.io compatible
✓ Dynamic PORT
✓ Safe backend imports
✓ Gemini optional
"""

import os
import sys
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# -------------------------------------------------------
# Ensure backend folder is importable (Railway compatible)
# -------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))     # /backend
ROOT_DIR = os.path.dirname(BASE_DIR)                      # project root
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# -------------------------------------------------------
# Select semantic model automatically
# Cloud → use lightweight
# Local PC → heavy model works
# -------------------------------------------------------
CLOUD = os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RENDER")
if CLOUD:
    print("🌐 Cloud detected → Using semantic_light")
    from backend.detectors.semantic import check_semantic
else:
    print("💻 Local environment → Using semantic_heavy")
    from semantic_heavy import check_semantic

# Patch analyzer to use correct semantic
from backend.detectors import analyzer
analyzer.check_semantic = check_semantic
from backend.detectors.analyzer import analyze_prompt

# -------------------------------------------------------
# Load env variables (Gemini optional)
# -------------------------------------------------------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("⚠ No GEMINI_API_KEY found — running in LOCAL MODE ONLY.\n")

# -------------------------------------------------------
# FastAPI App
# -------------------------------------------------------
app = FastAPI(
    title="PromptGuard API",
    version="2.0.2",
    description="AI Prompt Firewall combining rules + semantic analysis.",
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all (frontend will run on another domain)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------
# Request Model
# -------------------------------------------------------
class PromptRequest(BaseModel):
    prompt: str

# -------------------------------------------------------
# Routes
# -------------------------------------------------------
@app.get("/")
def health():
    return {"status": "OK", "message": "PromptGuard API is alive 🔥"}

@app.post("/analyze")
def analyze_route(data: PromptRequest):

    prompt = data.prompt
    analysis = analyze_prompt(prompt)

    # Block unsafe prompts
    if not analysis["final_safe"]:
        return {
            "safe": False,
            "analysis": analysis,
            "response": "🚫 Unsafe prompt blocked by PromptGuard.",
        }

    # If safe + Gemini not configured → local only
    if not API_KEY:
        return {
            "safe": True,
            "analysis": analysis,
            "response": "⚠ Gemini not configured — only local AI analysis executed.",
        }

    # If Gemini exists → call Gemini safely (REST API)
    try:
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

        headers = {"Content-Type": "application/json"}

        res = requests.post(f"{url}?key={API_KEY}", json=payload, headers=headers)

        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=res.text)

        g = res.json()
        text = (
            g.get("candidates", [{}])[0]
             .get("content", {})
             .get("parts", [{}])[0]
             .get("text", "⚠ Gemini returned no text.")
        )

        return {"safe": True, "analysis": analysis, "response": text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {e}")


# -------------------------------------------------------
# Local development runner (Railway ignores this)
# -------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 9000))   # Railway sets PORT automatically
    )
