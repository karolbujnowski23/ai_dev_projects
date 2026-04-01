import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.config')
load_dotenv(dotenv_path)

APIKEY = os.getenv("APIKEY")
GEMINI_APIKEY = os.getenv("GEMINI_APIKEY")
OPENROUTER_APIKEY = os.getenv("OPENROUTER_APIKEY")

CENTRALA_URL = "https://hub.ag3nts.org/verify"
OKO_URL = "https://oko.ag3nts.org/"
