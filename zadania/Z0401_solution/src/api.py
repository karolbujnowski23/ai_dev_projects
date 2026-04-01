import requests
import logging
import json
from src.config import APIKEY, CENTRALA_URL

logger = logging.getLogger("api")

def send_to_centrala(payload_answer):
    """Sends a payload to the centrala API."""
    url = CENTRALA_URL
    headers = {"Content-Type": "application/json"}
    payload = {
        "apikey": APIKEY,
        "task": "okoeditor",
        "answer": payload_answer
    }
    
    logger.info(f"Sending payload to {url}: {json.dumps(payload_answer)}")
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        logger.info(f"Received response: {response.text}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending payload to centrala: {e}")
        if e.response:
            logger.error(f"Response body: {e.response.text}")
        return {"error": str(e), "status_code": e.response.status_code if e.response else None}
