
import os

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise EnvironmentError("❌ GOOGLE_API_KEY not found in environment variables.")

print("*************************************************** ✅ Gemini API key setup complete.")
