import requests
import logging
from src.validation.tokenizer import is_within_limit

logger = logging.getLogger(__name__)

class HubClient:
    def __init__(self, endpoint: str, api_key: str):
        self.endpoint = endpoint
        self.api_key = api_key

    def send_prompt(self, prompt: str) -> dict:
        """Wysyła prompt do huba w celu weryfikacji."""
        payload = {
            "apikey": self.api_key,
            "task": "categorize",
            "answer": {
                "prompt": prompt
            }
        }
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(self.endpoint, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                try:
                    return e.response.json()
                except:
                    pass
            logger.error(f"Hub request failed: {e}")
            return {"code": -1, "message": str(e)}

    def send_reset(self) -> dict:
        """Wysyła polecenie resetujące licznik."""
        return self.send_prompt("reset")

def build_prompt_and_classify(items: list[dict], static_prompt_base: str, hub_client: HubClient) -> list[dict]:
    """
    Buduje prompt dla każdego towaru z osobna i wysyła do huba.
    """
    results = []
    
    for item in items:
        item_id = str(item.get('code', ''))
        description = str(item.get('description', ''))
        
        # 1. Zbudowanie finalnego promptu z danymi na końcu dla cachowania
        dynamic_data = f"\nID: {item_id} - {description}"
        final_prompt = static_prompt_base + dynamic_data
        
        # 2. Walidacja tokenów
        if not is_within_limit(final_prompt, 100):
            logger.warning(f"Prompt dla ID {item_id} przekracza 100 tokenów. Pomijanie.")
            results.append({"code": -1, "message": "Prompt too long", "item_id": item_id})
            continue
            
        # 3. Wysyłka samego promptu do huba, który wykonuje klasyfikację
        hub_resp = hub_client.send_prompt(final_prompt)
        logger.info(f"Raw hub response: {hub_resp}")
        
        # Dodanie ID dla łatwiejszej analizy błędów
        if isinstance(hub_resp, dict):
            hub_resp["item_id"] = item_id
            
        results.append(hub_resp)
        
        # Jeśli napotkaliśmy błąd budżetu lub błędną klasyfikację, przerywamy pętlę i zwracamy dotychczasowe błędy
        # aby nie marnować dalej budżetu (hub i tak wymaga resetu)
        if isinstance(hub_resp, dict) and hub_resp.get("code", 0) < 0:
            break
            
    return results
