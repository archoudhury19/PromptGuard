print("🔥 API STARTED FROM:", __file__)

"""
PromptGuard API — Cloud Deployment Ready (FINAL)
------------------------------------------------
✓ Auto-detects cloud → uses semantic_light + sanitizer_light
✓ Local PC → uses heavy MPNet + heavy sanitizer
✓ Fully Railway / Render / Fly.io compatible
✓ Dynamic PORT
"""

import os
import sys
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# ---------------------------------------------
# Ensure backend/ is importable (Railway safe)
# ---------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))     # /backend
ROOT_DIR = os.path.dirname(BASE_DIR)                      # project root
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# ---------------------------------------------
# AUTOMATIC CLOUD DETECTION
# ---------------------------------------------
IS_CLOUD = os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RENDER")

if IS_CLOUD:
    print("🌐 Cloud detected → Using semantic_light + sanitizer_light")
else:
    print("💻 Local environment detected → Using heavy semantic model")

# ---------------------------------------------
# Import analyzer (auto selects heavy/light)
# ---------------------------------------------
from backend.detectors.analyzer import analyze_prompt

# ---------------------------------------------
# Load environment variables
# ---------------------------------------------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("⚠ No GEMINI_API_KEY found — API will run in LOCAL MODE ONLY.\n")

# ---------------------------------------------
# FastAPI App
# ---------------------------------------------
app = FastAPI(
    title="PromptGuard API",
    version="3.0.0",
    description="AI Prompt Firewall combining rules + semantic + sanitizer auto-switching.",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------
# Request model
# ---------------------------------------------
class PromptRequest(BaseModel):
    prompt: str

# ---------------------------------------------
# Routes
# ---------------------------------------------
@app.get("/")
def health():
    return {"status": "OK", "message": "PromptGuard API is alive 🔥"}

@app.post("/analyze")
def analyze_route(data: PromptRequest):

    prompt = data.prompt
    analysis = analyze_prompt(prompt)

    # Unsafe prompt → block
    if not analysis["final_safe"]:
        return {
            "safe": False,
            "analysis": analysis,
            "response": "🚫 Unsafe prompt blocked by PromptGuard."
        }

    # Safe but no Gemini key
    if not API_KEY:
        return {
            "safe": True,
            "analysis": analysis,
            "response": "⚠ Gemini not configured — only local safety analysis done."
        }

    # Call Gemini REST API
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

        return {
            "safe": True,
            "analysis": analysis,
            "response": text
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {e}")

# ---------------------------------------------
# Local dev runner (not used in Railway)
# ---------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 9000))
    )
