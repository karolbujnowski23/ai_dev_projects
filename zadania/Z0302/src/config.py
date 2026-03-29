import os
from dotenv import load_dotenv

# Path to the config file relative to this script
config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.config'))

# Load environment variables from the .config file
load_dotenv(dotenv_path=config_path)

API_KEY = os.getenv('APIKEY')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_APIKEY')
GEMINI_API_KEY = os.getenv('GEMINI_APIKEY')

SHELL_URL = "https://hub.ag3nts.org/api/shell"
VERIFY_URL = "https://hub.ag3nts.org/verify"
TASK_NAME = "firmware"
