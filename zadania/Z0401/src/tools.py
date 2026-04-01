import json
import logging
import requests
from src.config import APIKEY, CENTRALA_URL

logger = logging.getLogger("tools")

def send_oko_action(action_payload: dict):
    payload = {
        "apikey": APIKEY,
        "task": "okoeditor",
        "answer": action_payload
    }
    logger.info(f"[Tool] Sending OKO action payload: {json.dumps(action_payload, ensure_ascii=False)}")
    r = requests.post(CENTRALA_URL, json=payload)
    if r.status_code != 200:
        try:
            error_json = r.json()
            logger.error(f"API Error Response: {json.dumps(error_json, indent=2, ensure_ascii=False)}")
        except json.JSONDecodeError:
            logger.error(f"API Error Response (raw text): {r.text}")
    r.raise_for_status()
    return r.json()

TOOLS = [
    {
        "functionDeclarations": [
            {
                "name": "send_oko_action",
                "description": "Send an action to the OKO API. Payload needs to be a valid JSON.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "action_payload": {
                            "type": "STRING",
                            "description": "A JSON string containing the object to send as 'answer' (e.g., {\"action\": \"help\"})."
                        }
                    },
                    "required": ["action_payload"]
                }
            }
        ]
    }
]

def execute_tool(name, args):
    if name == "send_oko_action":
        try:
            payload = json.loads(args["action_payload"])
            return json.dumps(send_oko_action(payload), ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error executing send_oko_action: {e}")
            return json.dumps({"error": str(e)})
    return json.dumps({"error": f"Unknown tool: {name}"})
