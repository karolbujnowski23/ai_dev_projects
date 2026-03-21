import os
from dotenv import load_dotenv

load_dotenv()

# App Configuration
APP_NAME = os.getenv("APP_NAME", "TemplateMCPApp")
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").lower()
WORKSPACE_DIR = os.getenv("WORKSPACE_DIR", "./workspace")
