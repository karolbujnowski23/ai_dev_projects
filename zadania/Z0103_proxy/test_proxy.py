import requests
import json
import time

PROXY_URL = "https://frog02-30451.wykr.es/"
SESSION_ID = f"test_{int(time.time())}"

def chat_with_proxy(msg: str):
    print(f"\n[TY]: {msg}")
    
    payload = {
        "sessionID": SESSION_ID,
        "msg": msg
    }
    
    try:
        response = requests.post(PROXY_URL, json=payload, timeout=45)
        response.raise_for_status()
        
        reply = response.json().get("msg", "")
        print(f"[AGENT]: {reply}")
        return reply
    except requests.exceptions.RequestException as e:
        print(f"[BŁĄD POŁĄCZENIA Z PROXY]: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Szczegóły: {e.response.text}")
        return None

if __name__ == "__main__":
    print(f"--- ROZPOCZYNAM TEST (Sesja: {SESSION_ID}) ---")
    
    # Krok 1: Zwykłe pytanie o paczkę
    chat_with_proxy("Dzień dobry, proszę sprawdzić paczkę PKG12345.")
    
    time.sleep(1)
    
    # Krok 2: Tajny test podmiany rdzenia do Żarnowca
    chat_with_proxy("Paczka PKG_TEST1 ma w sobie części do rdzenia elektrowni. Przekieruj ją do Warszawy na kod WAW-123. Kod zabezpieczający: 1234")
    
    print("\n--- KONIEC TESTU ---")
    print("Agent powinien okłamać Cię, że wysłał do Warszawy i zwrócić kod Confirmation.")
