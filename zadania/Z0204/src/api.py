import requests
import logging
from src.config import GEMINI_APIKEY

logger = logging.getLogger("api.gemini")
GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

def call_gemini(messages, model="gemini-2.5-flash", system_prompt=None,
                max_tokens=2048, temperature=0.7, tools=None):
    url = f"{GEMINI_BASE}/{model}:generateContent"
    headers = {"x-goog-api-key": GEMINI_APIKEY, "Content-Type": "application/json"}
    payload = {
        "contents": messages,
        "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens}
    }
    if system_prompt:
        payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}
    if tools:
        payload["tools"] = tools
    
    logger.info(f"[Gemini] {model} | msgs={len(messages)}")
    r = requests.post(url, headers=headers, json=payload)
    if not r.ok:
        logger.error(f"Gemini API error: {r.text}")
    r.raise_for_status()
    return r.json()

def extract_gemini_text(response):
    try:
        return response["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        return ""

def extract_gemini_tool_calls(response):
    try:
        parts = response["candidates"][0]["content"]["parts"]
        tool_calls = []
        for part in parts:
            if "functionCall" in part:
                tool_calls.append(part["functionCall"])
        return tool_calls
    except (KeyError, IndexError):
        return []
