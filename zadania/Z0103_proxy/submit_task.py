import requests
import json
import os
from dotenv import load_dotenv

# Wczytaj klucze z .env, jeśli tam są (lub ustaw ręcznie)
load_dotenv()
API_KEY = os.getenv("AGENT_API_KEY", "aef1bda3-8909-428e-986e-1042b1a197c7")

HUB_VERIFY_URL = "https://hub.ag3nts.org/verify"

payload = {
    "apikey": API_KEY,
    "task": "proxy",
    "answer": {
        "url": "https://frog02-30451.wykr.es/",
        "sessionID": "test_session_frog02_30451"
    }
}

print("Wysyłam zgłoszenie do Hub-a...")
try:
    response = requests.post(HUB_VERIFY_URL, json=payload, timeout=30)
    response.raise_for_status()
    
    print("\n--- ODPOWIEDŹ Z HUB-A ---")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except requests.exceptions.RequestException as e:
    print(f"\nBŁĄD: Nie udało się połączyć z Hub-em lub Hub zwrócił błąd: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Szczegóły błędu: {e.response.text}")
