import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.config"))

GEMINI_APIKEY = os.getenv("GEMINI_LLM_APIKEY")
OPENR_APIKEY  = os.getenv("LLM_APIKEY")
APIKEY        = os.getenv("APIKEY")
