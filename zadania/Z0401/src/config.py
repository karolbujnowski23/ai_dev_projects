import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.config"))

GEMINI_APIKEY = os.getenv("GEMINI_APIKEY")
OPENR_APIKEY  = os.getenv("OPENROUTER_APIKEY")
APIKEY        = os.getenv("APIKEY")
CENTRALA_URL  = "https://hub.ag3nts.org/verify"
