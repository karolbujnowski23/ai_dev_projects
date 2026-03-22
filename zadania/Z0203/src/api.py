import requests
import json
from src.config import GEMINI_API_KEY, APIKEY

def generate_content(prompt):
    """
    Sends a request to the Gemini API and returns the generated text.
    Requires GEMINI_API_KEY to be present in the .env file.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found in environment variables. Please check your config file.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    
    headers = {
        'x-goog-api-key': GEMINI_API_KEY,
        'Content-Type': 'application/json'
    }
    
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.ok:
            data = response.json()
            if 'candidates' in data and data['candidates']:
                candidate = data['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content'] and candidate['content']['parts']:
                    return candidate['content']['parts'][0]['text']
                else:
                    return "Received response without parts structure."
            else:
                return "No response received from the model (candidates list is empty)."
        else:
            return f"Gemini API Error ({response.status_code}): {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Gemini API: {str(e)}"
    except (KeyError, IndexError) as e:
        return f"Error parsing model response: {str(e)}\nRaw data: {data}"


def verify_logs(logs_content: str) -> dict:
    """
    Sends the condensed logs to the Central hub for verification.
    """
    if not APIKEY:
        raise ValueError("APIKEY not found in configuration.")

    url = "https://hub.ag3nts.org/verify"
    payload = {
        "apikey": APIKEY,
        "task": "failure",
        "answer": {
            "logs": logs_content
        }
    }

    try:
        response = requests.post(url, json=payload)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Verification API Error ({e})"}

if __name__ == '__main__':
    # Test connection to Gemini
    print("Testing connection to Gemini API...")
    test_prompt = "Explain how neural networks work in two sentences."
    try:
        response = generate_content(test_prompt)
        print("\nResponse from model:")
        print(response)
    except Exception as err:
        print(f"\nError: {err}")
