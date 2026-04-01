import requests, logging
from src.config import GEMINI_APIKEY, OPENR_APIKEY

logger = logging.getLogger("api")
GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
GEMINI_CACHE_NAME: str = None

def call_gemini(messages, model="gemini-3.1-pro-preview", system_prompt=None,
                max_tokens=2048, temperature=0.7, tools=None, use_cache=False):
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
    if use_cache and GEMINI_CACHE_NAME:
        payload["cachedContent"] = GEMINI_CACHE_NAME
        logger.info(f"Sending payload to {url}: {json.dumps(payload_answer, ensure_ascii=False)}")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload, ensure_ascii=False))
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
    return response.json()

def extract_gemini_text(response):
    try:
        return response["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        return None

def extract_gemini_tool_calls(response):
    try:
        parts = response["candidates"][0]["content"]["parts"]
        return [part["functionCall"] for part in parts if "functionCall" in part]
    except (KeyError, IndexError):
        return []

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def call_openrouter(messages, model="meta-llama/llama-3-70b-instruct", system_prompt=None,
                    max_tokens=2048, temperature=0.7, tools=None, tool_choice="auto",
                    response_format=None, plugins=None, use_cache=False):
    headers = {
        "Authorization": f"Bearer {OPENR_APIKEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/AI_devs",
        "X-Title": "AI Solver"
    }
    full_messages = []
    if system_prompt:
        full_messages.append({"role": "system", "content": system_prompt})
    full_messages.extend(messages)
    payload = {"model": model, "messages": full_messages,
               "max_tokens": max_tokens, "temperature": temperature}
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = tool_choice
    if response_format:
        payload["response_format"] = response_format
    active_plugins = list(plugins or [])
    if use_cache:
        active_plugins.append({"id": "context-compression"})
    if active_plugins:
        payload["plugins"] = active_plugins
    logger.info(f"[OpenRouter] {model} | msgs={len(full_messages)} cache={use_cache}")
    r = requests.post(OPENROUTER_URL, headers=headers, json=payload)
    r.raise_for_status()
    return r.json()

def extract_openrouter_text(response):
    return response["choices"][0]["message"]["content"]

def extract_openrouter_tool_calls(response):
    return response["choices"][0]["message"].get("tool_calls", [])
