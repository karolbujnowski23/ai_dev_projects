import requests
import json
import time
from src.config import GEMINI_APIKEY
from src.logger import logger

GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

def call_gemini(messages, model="gemini-2.5-flash", max_tokens=2048, temperature=0.7, system_prompt=None, retries=5):
    url = f"{GEMINI_BASE}/{model}:generateContent"
    headers = {"x-goog-api-key": GEMINI_APIKEY, "Content-Type": "application/json"}
    
    payload = {
        "contents": messages,
        "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens}
    }
    
    if system_prompt:
        payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}
        
    logger.debug(f"Calling Gemini API model={model}")
    
    delay = 2
    for attempt in range(retries):
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=60)
            r.raise_for_status()
            logger.debug(f"Gemini API Response: {r.text[:200]}...")
            return r.json()
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                status = e.response.status_code
                logger.error(f"Gemini API error on attempt {attempt + 1}: {status} - {e.response.text}")
                if status in [500, 503, 429]:
                    logger.warning(f"Server error {status}, retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2
                    continue
            else:
                logger.error(f"Gemini API connection error on attempt {attempt + 1}: {e}")
                time.sleep(delay)
                delay *= 2
                continue
            raise e
    raise Exception("Max retries exceeded for Gemini API.")

def extract_gemini_text(response):
    try:
        return response["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        return ""