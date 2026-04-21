import os
from dotenv import load_dotenv
from google import genai


load_dotenv()

def create_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")
    return genai.Client(api_key=api_key)

