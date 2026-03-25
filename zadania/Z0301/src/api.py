import requests
import json
import logging
import os
from .config import GEMINI_API_KEY, OPENROUTER_API_KEY, CENTRALA_URL

# Logging setup as per solver_prompt.md
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Orchestrator")

class GeminiClient:
    def __init__(self, model="gemini-3.1-flash-lite-preview"):
        self.api_key = GEMINI_API_KEY
        self.model = model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def call(self, system_prompt, user_prompt, use_cache=True):
        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "system_instruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt}]
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json"
            }
        }
        
        logger.info(f"Calling Gemini ({self.model}) with user prompt length: {len(user_prompt)}")
        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            content = result['candidates'][0]['content']['parts'][0]['text']
            logger.info("Successfully received Gemini response.")
            return json.loads(content)
        except Exception as e:
            logger.error(f"Error calling Gemini: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response body: {e.response.text}")
            return None

class CentralaClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = CENTRALA_URL

    def submit(self, task_name, answer):
        payload = {
            "apikey": self.api_key,
            "task": task_name,
            "answer": answer
        }
        logger.info(f"Submitting task {task_name} to {self.url}")
        try:
            response = requests.post(self.url, json=payload)
            response.raise_for_status()
            logger.info(f"Submission successful. Response: {response.json()}")
            return response.json()
        except Exception as e:
            logger.error(f"Error submitting task: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response body: {e.response.text}")
            return None
