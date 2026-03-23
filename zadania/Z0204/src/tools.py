import requests
import logging
from src.config import APIKEY

logger = logging.getLogger("tools")

HUB_URL = "https://hub.ag3nts.org"

def call_zmail_api(action: str, **kwargs):
    """
    Communicates with zmail API at https://hub.ag3nts.org/api/zmail.
    """
    url = f"{HUB_URL}/api/zmail"
    payload = {
        "apikey": APIKEY,
        "action": action,
    }
    payload.update(kwargs)
    
    logger.info(f"Calling zmail API: action={action}, params={kwargs}")
    r = requests.post(url, json=payload)
    if not r.ok:
        logger.error(f"Zmail API error: {r.text}")
    r.raise_for_status()
    return r.json()

def submit_verification(date: str, password: str, confirmation_code: str):
    """
    Submits the final answer to https://hub.ag3nts.org/verify.
    """
    url = f"{HUB_URL}/verify"
    payload = {
        "apikey": APIKEY,
        "task": "mailbox",
        "answer": {
            "date": date,
            "password": password,
            "confirmation_code": confirmation_code
        }
    }
    
    logger.info(f"Calling verify: answer={payload['answer']}")
    r = requests.post(url, json=payload)
    if not r.ok:
        logger.error(f"Verify API error: {r.text}")
    r.raise_for_status()
    return r.json()

# Gemini Tool Declarations
TOOLS = [
    {
        "functionDeclarations": [
            {
                "name": "call_zmail_api",
                "description": "Calls the zmail API to interact with the mailbox. First use 'help' action to find available actions and parameters.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "action": {
                            "type": "STRING",
                            "description": "The action to perform, e.g. 'help', 'getInbox', etc."
                        },
                        "page": {
                            "type": "INTEGER",
                            "description": "Page number (optional, often defaults to 1)."
                        },
                        "query": {
                            "type": "STRING",
                            "description": "Search query if applicable."
                        },
                        "id": {
                            "type": "STRING",
                            "description": "Message ID if fetching a specific message."
                        }
                    },
                    "required": ["action"]
                }
            },
            {
                "name": "submit_verification",
                "description": "Submits the final extracted answers to the verification endpoint.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "date": {
                            "type": "STRING",
                            "description": "The date when the security department plans to attack the power plant (format YYYY-MM-DD)."
                        },
                        "password": {
                            "type": "STRING",
                            "description": "The password for the employee system."
                        },
                        "confirmation_code": {
                            "type": "STRING",
                            "description": "The confirmation code from the ticket sent by the security department (format: SEC- + 32 characters)."
                        }
                    },
                    "required": ["date", "password", "confirmation_code"]
                }
            }
        ]
    }
]
