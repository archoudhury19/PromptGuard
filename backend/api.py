print("🔥 API STARTED FROM:", __file__)

"""
PromptGuard API — Cloud Deployment Ready (FINAL)
------------------------------------------------
✓ Auto-detects cloud → semantic_light + sanitizer_light
✓ Local PC → semantic_heavy + sanitizer_heavy
✓ Analyzer always uses the correct engines (patched)
✓ Fully Railway / Render compatible
✓ Dynamic PORT
"""

import os
import sys
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv


# -------------------------------------------------------------
# Ensure backend/ is importable
# -------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # /backend
ROOT_DIR = os.path.dirname(BASE_DIR)
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)


# -------------------------------------------------------------
# Accurate Cloud Detection (Fixed)
# -------------------------------------------------------------
def detect_cloud():
    is_railway = (
        os.getenv("RAILWAY_ENVIRONMENT") == "production"
        or os.getenv("RAILWAY_ENVIRONMENT") == "true"
    )

    is_render = (
        os.getenv("RENDER_SERVICE_ID") is not None
        or os.getenv("RENDER_EXTERNAL_URL") is not None
        or os.getenv("RENDER") == "true"
    )

    return is_railway or is_render


CLOUD = detect_cloud()


# -------------------------------------------------------------
# Import correct semantic + sanitizer based on environment
# -------------------------------------------------------------
if CLOUD:
    print("🌐 Cloud detected → Using semantic_light + sanitizer_light")
    from backend.detectors.semantic_light import check_semantic
    from backend.detectors.sanitizer_light import sanitize_prompt
else:
    print("💻 Local Mode → Using semantic_heavy + sanitizer_heavy")
    from backend.detectors.semantic_heavy import check_semantic
    from backend.detectors.sanitizer_heavy import sanitize_prompt


# -------------------------------------------------------------
# Patch analyzer to use selected engines
# -------------------------------------------------------------
from backend.detectors import analyzer
analyzer.check_semantic = check_semantic
analyzer.sanitize_prompt = sanitize_prompt
from backend.detectors.analyzer import analyze_prompt


# -------------------------------------------------------------
# Load environment variables
# -------------------------------------------------------------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("⚠ No GEMINI_API_KEY found — running in LOCAL MODE ONLY.\n")


# -------------------------------------------------------------
# FastAPI app
# -------------------------------------------------------------
app = FastAPI(
    title="PromptGuard API",
    version="3.0.1",
    description="AI Prompt Firewall | Autoswitch semantic + sanitizer engines",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------
# Request model
# -------------------------------------------------------------
class PromptRequest(BaseModel):
    prompt: str


# -------------------------------------------------------------
# Routes
# -------------------------------------------------------------
@app.get("/")
def health():
    return {"status": "OK", "mode": "cloud" if CLOUD else "local", "message": "PromptGuard API is running 🔥"}


@app.post("/analyze")
def analyze_route(data: PromptRequest):

    prompt = data.prompt
    analysis = analyze_prompt(prompt)

    # Unsafe → block early
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
            "response": "⚠ Gemini not configured — only local analysis executed."
        }

    # Call Gemini API
    try:
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        payload = { "contents": [ { "parts": [ { "text": prompt } ] } ] }
        headers = { "Content-Type": "application/json" }

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


# -------------------------------------------------------------
# Local runner
# -------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 9000))
    )
