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

if __name__ == '__main__':
    # Example usage
    print("getting help...")

    """ 
    mail_actions={}
    for i in range(20):
        if i > 0 and (not result.get('actions') or 'error' in result):
            break
        print(f"Getting page {i+1} of mail actions...")
        result = get_mail(action='help', page=i+1)
        mail_actions.update(result['actions'])
        # print(json.dumps(result, indent=2))
        print([*result['actions']])
    
    # result = get_mail(action='help', page=2)
    # print(json.dumps(result['actions'], indent=2))
    print(json.dumps(mail_actions, indent=2))
    print([*mail_actions])
    """
    
    print(json.dumps(get_mail(action='help', page=1), indent=2))
    print(json.dumps(get_mail(action='help', page=5), indent=2))
    

    

    