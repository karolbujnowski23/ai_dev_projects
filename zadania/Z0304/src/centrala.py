import requests
import time
from .config import APIKEY
from .helpers.logger import log

def submit_tools_to_verify(tool_definitions: list) -> dict:
    """
    Submits tool definitions to the /verify endpoint.
    """
    url = "https://hub.ag3nts.org/verify"
    payload = {
        "apikey": APIKEY,
        "task": "negotiations",
        "answer": {
            "tools": tool_definitions
        }
    }
    
    log.info(f"Submitting tools to {url}...")
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            log.error(f"Failed to submit tools: {response.status_code} - {response.text}")
            return {}
        result = response.json()
        log.success(f"Tools submitted successfully: {result}")
        return result
    except Exception as e:
        log.error(f"Exception during tool submission: {e}")
        return {}

def check_verification_status() -> dict:
    """
    Checks the status of verification and retrieves the flag.
    """
    url = "https://hub.ag3nts.org/verify"
    payload = {
        "apikey": APIKEY,
        "task": "negotiations",
        "answer": {
            "action": "check"
        }
    }
    
    log.info(f"Checking verification status at {url}...")
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            log.error(f"Failed to check status: {response.status_code} - {response.text}")
            return {}
        result = response.json()
        log.info(f"Verification status: {result}")
        return result
    except Exception as e:
        log.error(f"Exception during status check: {e}")
        return {}

def orchestrate_verification(tool_definitions: list, wait_seconds: int = 40):
    """
    Submits tools, waits the required asynchronous time, and checks the status.
    """
    submit_tools_to_verify(tool_definitions)
    
    log.info(f"Waiting {wait_seconds} seconds for the agent to process our tools...")
    time.sleep(wait_seconds)
    
    return check_verification_status()