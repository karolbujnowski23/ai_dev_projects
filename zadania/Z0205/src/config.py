import os
from dotenv import load_dotenv

config_path = os.path.join(os.path.dirname(__file__), '..', '..', '.config')
load_dotenv(config_path)

GEMINI_APIKEY = os.getenv("GEMINI_LLM_APIKEY")
APIKEY = os.getenv("APIKEY")

if GEMINI_APIKEY:
    GEMINI_APIKEY = GEMINI_APIKEY.strip(' "') # Strip spaces and quotes

if not GEMINI_APIKEY:
    print("WARNING: GEMINI_LLM_APIKEY is not set.")
if not APIKEY:
    print("WARNING: APIKEY is not set.")
