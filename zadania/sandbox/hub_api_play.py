import requests
import json
from dotenv import load_dotenv
import os

load_dotenv('./zadania/.config')
APIKEY = os.getenv("APIKEY")

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
    
def get_mail(action: str, page: int) -> dict:
    """
    Sends the condensed logs to the Central hub for verification.
    """
    if not APIKEY:
        raise ValueError("APIKEY not found in configuration.")

    url = "https://hub.ag3nts.org/api/zmail"
    payload = {
        "apikey": APIKEY,
        "action": action,
        "page": page
        }
    
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Verification API Error ({e})"}

def drone(instructions: list) -> dict:
    """
    Example function to demonstrate how to call the zmail API.
    """
    url = "https://hub.ag3nts.org/verify"
    payload = {
        "apikey": APIKEY,
        "task": "drone",
        "answer": {
            "instructions": instructions
        }
    }
    try:
        response = requests.post(
            url, json=payload)

        result = response.json()
    except requests.exceptions.RequestException as e:
        result = {"error": f"API Error ({e})"}

    return json.dumps(result, indent=2)
if __name__ == '__main__':
    # Example usage
    print("setting drone...")

    self_check = [
      "calibrateGPS",
      "calibrateCompass",
      "selfCheck",
      "setDestinationObject(PWR6132PL)",
      "set(2,4)",
      "set(100m)",
      "set(engineON)",
      "set(10%)",
      "set(image)",
      "set(destroy)",
      "set(return)",
      "flyToLocation"
        ]
    set_name = ["setName(Orzel 7)"]
    
    result = drone(self_check)
    print(f"self check result: {result}")


    