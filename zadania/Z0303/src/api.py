import requests
import json
import logging
from .config import API_KEY, GEMINI_API_KEY, OPENROUTER_API_KEY, VERIFY_URL, TASK_NAME

logger = logging.getLogger("API")

def call_verify(command: str) -> dict:
    payload = {
        "apikey": API_KEY,
        "task": TASK_NAME,
        "answer": {
            "command": command
        }
    }
    logger.info(f"VERIFY Request: {command}")
    response = requests.post(VERIFY_URL, json=payload)
    try:
        result = response.json()
        logger.info(f"VERIFY Response: {result}")
        return result
    except Exception as e:
        logger.error(f"Failed to parse verify response: {response.text}")
        return {"error": str(e), "raw": response.text}

def call_llm(messages: list, system_prompt: str = "", model: str = "gemini-2.5-flash", tools: list = None) -> dict:
    """
    Call Gemini API directly using requests.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }
    
    # SANITIZE MESSAGES for Gemini API
    # Gemini only accepts 'role' and 'parts'. 'role' must be 'user' or 'model'.
    # It strictly rejects unknown fields like 'content'.
    sanitized_contents = []
    for msg in messages:
        role = msg.get("role", "user")
        if role in ["assistant", "model"]:
            role = "model"
        else:
            role = "user"
            
        parts = msg.get("parts", [])
        if not parts and "content" in msg:
            parts = [{"text": str(msg["content"])}]
            
        sanitized_contents.append({
            "role": role,
            "parts": parts
        })
    
    payload = {
        "contents": sanitized_contents,
        "system_instruction": {
            "parts": [{"text": system_prompt}]
        } if system_prompt else None,
        "generationConfig": {
            "maxOutputTokens": 256
        }
    }
    
    if tools:
        payload["tools"] = [{"functionDeclarations": tools}]
        
    # Remove system_instruction if it's None
    if not payload["system_instruction"]:
        del payload["system_instruction"]
        
    logger.info(f"LLM Request: {model}")
    response = requests.post(url, json=payload, headers=headers)
    
    try:
        result = response.json()
        if "candidates" in result and result["candidates"]:
            candidate = result["candidates"][0]
            parts = candidate.get("content", {}).get("parts", [])
            
            output_msg = {"role": "model", "parts": parts}
            
            # For compatibility with app.py logic that expects 'content' key
            text_parts = [p["text"] for p in parts if "text" in p]
            if text_parts:
                output_msg["content"] = "\n".join(text_parts)
            else:
                output_msg["content"] = ""
                
            # Handle tool calls (functionCall)
            tool_calls = []
            for p in parts:
                if "functionCall" in p:
                    fc = p["functionCall"]
                    tool_calls.append({
                        "name": fc["name"],
                        "args": fc.get("args", {})
                    })
            if tool_calls:
                output_msg["tool_calls"] = tool_calls
                
            return output_msg
        else:
            logger.error(f"Unexpected LLM response: {result}")
            # Do NOT include the full result if it's huge, but we need to see the error
            return {"role": "model", "content": f"Error: {json.dumps(result)}"}
    except Exception as e:
        logger.error(f"Failed to parse LLM response: {response.text}")
        return {"role": "model", "content": f"Error: {str(e)}"}
