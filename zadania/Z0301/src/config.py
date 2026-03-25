import os
from dotenv import load_dotenv

# Path to the config file relative to this script
config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.config'))

# Load environment variables from the .config file
load_dotenv(dotenv_path=config_path)

API_KEY = os.getenv('APIKEY')
OPENROUTER_API_KEY = os.getenv('LLM_APIKEY')
GEMINI_API_KEY = os.getenv('GEMINI_LLM_APIKEY')

# Model configurations
MODEL_CONFIG = {
    "classifier": "gemini-3-pro-preview"
}

CENTRALA_URL = "https://hub.ag3nts.org/verify"
TASK_NAME = "evaluation"
