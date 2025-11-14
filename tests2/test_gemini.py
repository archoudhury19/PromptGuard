import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print("Loaded API Key:", api_key)

# Configure Gemini
genai.configure(api_key=api_key)

try:
    model = genai.GenerativeModel("gemini-pro")  # free tier model
    response = model.generate_content("Say Hello if you're working.")
    print("Gemini Response:", response.text)
except Exception as e:
    print("Error:", e)
