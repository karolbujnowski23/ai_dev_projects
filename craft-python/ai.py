import os
import requests

def chat(input_data, tools):
    api_key = os.getenv("OPENAI_API_KEY")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-4o",
        "input": input_data,
        "tools": tools
    }
    
    response = requests.post(
        "https://api.openai.com/v1/responses",
        headers=headers,
        json=payload
    )
    response.raise_for_status()
    data = response.json()
    
    output = data.get("output", [])
    
    message_obj = next((o for o in output if o.get("type") == "message"), None)
    calls = [o for o in output if o.get("type") == "function_call"]
    
    message = None
    if message_obj and "content" in message_obj and len(message_obj["content"]) > 0:
        message = message_obj["content"][0].get("text")
        
    return {
        "message": message,
        "calls": calls,
        "output": output
    }