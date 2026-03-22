import requests
import json
from config import GEMINI_LLM_APIKEY

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

def generate_content(prompt, system_instruction=None, tools=None):
    headers = {
        "x-goog-api-key": GEMINI_LLM_APIKEY,
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ]
    }

    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }
        
    if tools:
        payload["tools"] = tools

    response = requests.post(GEMINI_API_URL, headers=headers, json=payload)
    
    if response.status_code != 200:
        print(f"Error calling Gemini API: {response.text}")
        return None
        
    data = response.json()
    try:
        candidate = data['candidates'][0]
        content = candidate['content']
        parts = content.get('parts', [])
        
        # Check for tool call
        for part in parts:
            if 'functionCall' in part:
                return part['functionCall']
            
        # Return text if no tool call
        return parts[0]['text']
    except (KeyError, IndexError) as e:
        print(f"Failed to parse Gemini API response: {data}")
        return None

def verify_logs(apikey, logs_content):
    url = "https://hub.ag3nts.org/verify"
    payload = {
        "apikey": apikey,
        "task": "failure",
        "answer": {
            "logs": logs_content
        }
    }
    
    response = requests.post(url, json=payload)
    return response.json()
