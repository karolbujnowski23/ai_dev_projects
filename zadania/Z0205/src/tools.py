import requests
import json
from src.config import APIKEY
from src.logger import logger

def drone_verify(instructions: list) -> dict:
    if not APIKEY:
        raise ValueError("APIKEY not found in configuration.")

    url = "https://hub.ag3nts.org/verify"
    payload = {
        "apikey": APIKEY,
        "task": "drone",
        "answer": {
            "instructions": instructions
        }
    }
    
    logger.debug(f"Sending to /verify: {json.dumps(payload)}")

    try:
        response = requests.post(url, json=payload, timeout=30)
        logger.debug(f"/verify Response: {response.text}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Verification API Error: {e}")
        return {"error": f"Verification API Error ({e})"}