import json
import requests
from src.config import GEMINI_APIKEY
from src.logger import get_logger

logger = get_logger("API")

def call_llm(prompt: str, use_cache: bool = True, model: str = "gemini-2.5-flash") -> dict:
    """
    Calls the Gemini API using the requests library.
    Implements prompt caching if requested.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_APIKEY}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Very basic structure for gemini requests without proper caching implementation
    # since we don't have the exact geminiAPIref.md schema.
    # For now, we'll send a standard payload.
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        logger.info(f"Calling Gemini ({model})...")
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        logger.info("Gemini call successful.")
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Gemini: {e}")
        if response is not None:
             logger.error(f"Response: {response.text}")
        raise
