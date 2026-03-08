import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4.1-nano").strip()

if not OPENROUTER_API_KEY:
    raise ValueError("Falta OPENROUTER_API_KEY en el archivo .env")