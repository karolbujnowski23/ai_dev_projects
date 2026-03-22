import os

def load_config():
    config = {}
    config_path = os.path.join(os.path.dirname(__file__), '..', '.config')
    if not os.path.exists(config_path):
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', '.config')
        
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, val = line.split('=', 1)
                        config[key.strip()] = val.strip().strip('"').strip("'")
    return config

config = load_config()
APIKEY = config.get('APIKEY', '')
GEMINI_LLM_APIKEY = config.get('GEMINI_LLM_APIKEY', '')
