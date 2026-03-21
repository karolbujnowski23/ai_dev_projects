import json
import base64
import requests
from typing import Dict, Any

from src.config import GEMINI_API_KEY, APIKEY
from src.prompts.vision_prompt import VISION_PROMPT_FULL_BOARD

API_URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

def get_board_image_url() -> str:
    return f"https://hub.ag3nts.org/data/{APIKEY}/electricity.png"

def get_target_image_url() -> str:
    return "https://hub.ag3nts.org/i/solved_electricity.png"

def analyze_board_image(image_url: str) -> Dict[str, list[str]]:
    """
    Analizuje obraz planszy używając modelu Gemini i zwraca słownik połączeń pól.
    Wykorzystuje model gemini-3.1-pro-preview do analizy CAŁEGO obrazu,
    który jest bardziej precyzyjny niż małe wycinki jeśli nie znamy koordynatów planszy.
    """
    if not GEMINI_API_KEY:
        raise ValueError("Brak klucza GEMINI_API_KEY w zmiennych środowiskowych.")

    # Pobieranie obrazka
    img_resp = requests.get(image_url)
    img_resp.raise_for_status()
    image_data = img_resp.content
    
    encoded_image = base64.b64encode(image_data).decode("utf-8")
    
    mime_type = "image/png"
    if image_url.lower().endswith(".jpg") or image_url.lower().endswith(".jpeg"):
        mime_type = "image/jpeg"
    elif image_url.lower().endswith(".webp"):
        mime_type = "image/webp"

    url = API_URL_BASE.format(model="gemini-3.1-pro-preview")
    
    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [{
            "parts": [
                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": encoded_image
                    }
                },
                {"text": VISION_PROMPT_FULL_BOARD}
            ]
        }]
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    
    data = response.json()
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        if text.startswith("```json"): text = text[7:]
        if text.endswith("```"): text = text[:-3]
        return json.loads(text.strip())
    except Exception as e:
        print(f"Error parsing Gemini response: {e}, Response: {data}")
        return {}


def compare_board_states(target_state: Dict[str, list[str]], current_state: Dict[str, list[str]]) -> Dict[str, int]:
    """
    Porównuje dwa stany planszy matematycznie i oblicza ilość 
    obrotów o 90 stopni w prawo (!) dla każdego elementu z listy stan bieżący, 
    aby uzyskać stan docelowy. 
    Zwraca słownik {tile_id: rotacje}
    """
    directions = ["top", "right", "bottom", "left"]
    rotations_needed = {}
    
    for tile_id in target_state:
        target_edges = target_state[tile_id]
        curr_edges = current_state.get(tile_id, [])
        
        # Odrzuć błąd w którym brakuje różnicy
        if not curr_edges:
            rotations_needed[tile_id] = 0
            continue
            
        found_match = False
        for rotations in range(4):
            rotated = []
            for edge in curr_edges:
                if edge in directions:
                    idx = directions.index(edge)
                    rotated.append(directions[(idx + rotations) % 4])
                else:
                    rotated.append(edge) # Fallback ignorujący złe krawędzie
            
            if set(rotated) == set(target_edges):
                rotations_needed[tile_id] = rotations
                found_match = True
                break
                
        if not found_match:
            print(f"Brak dopasowania dla {tile_id}. Docelowo: {target_edges}, Obecnie: {curr_edges}")
            rotations_needed[tile_id] = 0 # Bezpieczny fallback - nie psujemy bardziej jeśli Gemini źle rozpoznał

    return rotations_needed

def rotate_tile(tile_id: str) -> Dict[str, Any]:
    """Wysyła zapytanie na serwer by obrócić płytkę na planszy o 90 stopni w prawo."""
    url = "https://hub.ag3nts.org/verify"
    payload = {
        "apikey": APIKEY,
        "task": "electricity",
        "answer": {
            "rotate": tile_id
        }
    }
    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    return resp.json()

def reset_board() -> str:
    """Zwraca planszę do początkowego stanu."""
    url = f"https://hub.ag3nts.org/data/{APIKEY}/electricity.png?reset=1"
    resp = requests.get(url)
    resp.raise_for_status()
    return "Plansza zresetowana."
