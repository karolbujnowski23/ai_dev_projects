import os
from dotenv import load_dotenv

load_dotenv("C:/Users/buyak/Documents/AI_devs/zadania/.config")

GEMINI_API_KEY = os.getenv("GEMINI_LLM_APIKEY")
APIKEY = os.getenv("APIKEY")
