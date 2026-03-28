import os
from pathlib import Path
from dotenv import load_dotenv

# Define search paths for .config
# 1. src/.config
# 2. Z0304/.config (current task folder)
# 3. zadania/.config (root folder)
current_dir = Path(__file__).parent
paths_to_try = [
    current_dir / ".config",
    current_dir.parent / ".config",
    current_dir.parent.parent / ".config"
]

config_loaded = False
for path in paths_to_try:
    if path.exists():
        load_dotenv(path)
        config_loaded = True
        break

def get_env_string(key):
    val = os.getenv(key)
    if val is None or val == "":
        raise ValueError(f"{key} is missing from configuration. Checked paths: {[str(p) for p in paths_to_try]}")
    # Strip potential quotes often found in .config files
    return val.strip('"').strip("'")

APIKEY = get_env_string("APIKEY")
GEMINI_APIKEY = get_env_string("GEMINI_APIKEY")
OPENROUTER_APIKEY = get_env_string("OPENROUTER_APIKEY")

API_CONFIG = {
    "model": "google/gemini-2.5-flash",
    "instructions": "Jesteś asystentem AI rozwiązującym zadania."
}

SERVER_PORT = int(os.getenv("SERVER_PORT", 20451))
