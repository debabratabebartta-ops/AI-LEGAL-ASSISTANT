from dotenv import load_dotenv
from google import genai
import os

# Load API key from .env file
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("API key not found. Check your .env file.")

else:
    try:
        # Connect to Gemini
        client = genai.Client(api_key=api_key)

        # Send a test request
        response = client.interactions.create(
            model="gemini-3.5-flash-lite",
            input="Introduce yourself in one simple sentence."
        )

        print("\nGemini API Connected Successfully!")
        print("Gemini Response:", response.output_text)

    except Exception as e:
        print("\nConnection Error:", e)