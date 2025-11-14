# test_api.py
"""
FastAPI entry point for PromptGuard.
Connects the analyzer pipeline to HTTP endpoints.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.detectors.analyzer import analyze_prompt

# -------------------------------------------------------------------------
# App Configuration
# -------------------------------------------------------------------------
app = FastAPI(
    title="PromptGuard API",
    description="Prompt injection and safety analysis backend.",
    version="1.0.0",
)

# Allow CORS for local or web frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------------
# Request Model
# -------------------------------------------------------------------------
class PromptInput(BaseModel):
    prompt: str

# -------------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------------
@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"message": "✅ PromptGuard API is running successfully!"}


@app.post("/analyze")
def analyze(input_data: PromptInput):
    """
    Analyze a user prompt and return safety results.
    """
    try:
        result = analyze_prompt(input_data.prompt)
        return {"status": "success", "analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
