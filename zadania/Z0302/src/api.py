import requests
import json
import logging
from src.config import API_KEY, GEMINI_API_KEY, OPENROUTER_API_KEY

logger = logging.getLogger("API")

def call_shell(cmd: str) -> dict:
    payload = {
        "apikey": API_KEY,
        "cmd": cmd
    }
    logger.info(f"Shell CMD: {cmd}")
    response = requests.post("https://hub.ag3nts.org/api/shell", json=payload)
    try:
        result = response.json()
        logger.info(f"Shell Response: {result}")
        return result
    except Exception as e:
        logger.error(f"Failed to parse shell response: {response.text}")
        return {"error": str(e), "raw": response.text}

def call_llm(messages: list, system_prompt: str = "", model: str = "anthropic/claude-3.5-sonnet", tools: list = None) -> dict:
    if "gemini" in model and GEMINI_API_KEY:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        
        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": f"SYSTEM: {system_prompt}"}]})
            contents.append({"role": "model", "parts": [{"text": "Understood."}]})
            
        for msg in messages:
            role = "user" if msg["role"] in ["user", "tool"] else "model"
            parts = []
            
            if msg.get("content"):
                parts.append({"text": str(msg["content"])})
                
            if "tool_calls" in msg and msg["tool_calls"]:
                for tc in msg["tool_calls"]:
                    args = tc["function"].get("arguments", "{}")
                    try:
                        args_dict = json.loads(args)
                    except:
                        args_dict = {}
                    parts.append({
                        "functionCall": {
                            "name": tc["function"]["name"],
                            "args": args_dict
                        }
                    })
                    
            if msg["role"] == "tool":
                parts.append({
                    "functionResponse": {
                        "name": msg.get("name", ""),
                        "response": {"result": msg.get("content", "")}
                    }
                })
                
            if parts:
                contents.append({"role": role, "parts": parts})
                
        payload = {"contents": contents}
        
        if tools:
            gemini_tools = [{"functionDeclarations": [t["function"] for t in tools]}]
            payload["tools"] = gemini_tools

        response = requests.post(url, json=payload, headers=headers)
        
        try:
            result = response.json()
            if "candidates" in result and result["candidates"]:
                candidate = result["candidates"][0]
                parts = candidate["content"]["parts"]
                
                output_msg = {"role": "assistant"}
                
                text_parts = [p["text"] for p in parts if "text" in p]
                if text_parts:
                    output_msg["content"] = "\n".join(text_parts)
                    
                tool_calls = []
                for p in parts:
                    if "functionCall" in p:
                        fc = p["functionCall"]
                        tool_calls.append({
                            "id": "call_" + fc["name"],
                            "type": "function",
                            "function": {
                                "name": fc["name"],
                                "arguments": json.dumps(fc.get("args", {}))
                            }
                        })
                if tool_calls:
                    output_msg["tool_calls"] = tool_calls
                    
                return output_msg
            else:
                logger.error(f"LLM Error: {result}")
                return {"role": "assistant", "content": str(result)}
        except Exception as e:
            logger.error(f"LLM API Call failed: {e}")
            return {"role": "assistant", "content": f"API Error: {str(e)}"}
    else:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)
        
        payload = {
            "model": model,
            "messages": full_messages
        }
        if tools:
            payload["tools"] = tools

        response = requests.post(url, json=payload, headers=headers)

        try:
            result = response.json()
            if "choices" in result:
                return result["choices"][0]["message"]
            else:
                logger.error(f"LLM Error: {result}")
                return {"role": "assistant", "content": str(result)}
        except Exception as e:
            logger.error(f"LLM API Call failed: {e}")
            return {"role": "assistant", "content": f"API Error: {str(e)}"}

def verify_task(answer: str):
    payload = {
        "apikey": API_KEY,
        "task": "firmware",
        "answer": {"confirmation": answer}
    }
    logger.info(f"Verifying task: {payload}")
    response = requests.post("https://hub.ag3nts.org/verify", json=payload)
    return response.json()
