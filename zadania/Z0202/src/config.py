import os
from dotenv import load_dotenv

load_dotenv("C:/Users/buyak/Documents/AI_devs/zadania/.config")

# App Configuration
APP_NAME = os.getenv("APP_NAME", "TemplateMCPApp")
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").lower()
WORKSPACE_DIR = os.getenv("WORKSPACE_DIR", "./workspace")

GEMINI_API_KEY = os.getenv("GEMINI_LLM_APIKEY")
APIKEY = os.getenv("APIKEY")
