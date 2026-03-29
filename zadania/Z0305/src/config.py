import os
from dotenv import load_dotenv

# Load environment variables from the parent .config file
config_path = os.path.join(os.path.dirname(__file__), '..', '..', '.config')
load_dotenv(config_path)

APIKEY = os.getenv("APIKEY")
GEMINI_APIKEY = os.getenv("GEMINI_APIKEY")
OPENR_APIKEY = os.getenv("OPENROUTER_APIKEY")

if not APIKEY:
    print("WARNING: APIKEY not found in .config")
if not GEMINI_APIKEY:
    print("WARNING: GEMINI_APIKEY not found in .config")
