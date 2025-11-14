import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def ask_gemini_safe(prompt: str):
    try:
        # ✅ Use free tier-supported model
        model = genai.GenerativeModel("gemini-pro")

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"Error using Gemini API: {str(e)}"
