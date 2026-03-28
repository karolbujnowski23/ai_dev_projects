import json
import requests
from typing import List, Dict, Any, Optional
from .config import GEMINI_APIKEY
from .helpers.logger import log

def extract_items_with_llm(query: str, available_items: List[str]) -> List[str]:
    """
    Call Gemini's API directly to extract items, bypassing inflections.
    """
    
    headers = {
        "Content-Type": "application/json"
    }

    prompt = f"""
    Jesteś systemem tłumaczącym zapytania w języku naturalnym na dokładne identyfikatory (nazwy) produktów z bazy danych.
    Twoim zadaniem jest przeanalizować wypowiedź użytkownika, wyłapać o jakie przedmioty mu chodzi (może ich być kilka), a następnie zwrócić DOKŁADNE NAZWY tych przedmiotów, skopiowane 1:1 z poniższej listy dopuszczalnych wartości.

    PRZYKŁADY:
    User: "Potrzebuję turbiny wiatrowej mającej 48V i moc 400W" -> Model: ["turbina wiatrowa 400w 48v"]
    User: "kabla długości 10 metrów i śmigła" -> Model: ["kabel 10m", "smiglo"] (przykładowo, jeśli takie są na liście)

    Baza dostępnych przedmiotów (zwracaj tylko nazwy występujące na tej liście, ignorując wielkość liter):
    {available_items}
    
    ZASADY:
    - Zwróć TYLKO poprawny format JSON (tablica stringów), bez żadnego dodatkowego tekstu.
    - Zwracaj DOKŁADNE nazwy z powyższej listy, w tym samym formacie. Jeśli na liście jest "turbina wiatrowa 400w 48v", nie zwracaj "turbina wiatrowa 48v i moc 400w".
    - Nie używaj znaczników markdown (```json).
    - Jeśli zapytanie nie pasuje do żadnego z przedmiotów z bazy, zwróć [].
    
    Wypowiedź użytkownika: {query}
    """
    
    body = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0
        }
    }
    
    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-pro-preview:generateContent?key={GEMINI_APIKEY}",
            headers=headers,
            json=body
        )
        response.raise_for_status()
        
        data = response.json()
        content = data['candidates'][0]['content']['parts'][0]['text'].strip()
        
        # Cleanup
        content = content.replace("```json", "").replace("```", "").strip()
        
        extracted_items = json.loads(content)
        if isinstance(extracted_items, list):
            return [str(item).lower() for item in extracted_items]
        return []
        
    except Exception as e:
        log.error(f"LLM extraction failed: {e}")
        return []

def send_to_centrala(payload: dict) -> dict:
    url = "https://centrala.ag3nts.org/report" # W Z0104 to jest używane. Sprawdzimy dokumentację do Z0304 dla dokładnego endpointu `/verify`
    # Z zadania wiemy, że musimy pisać pod endpoint /verify, prawdopodobnie chodzi o raport. Zróbmy więc to elastycznie
    pass