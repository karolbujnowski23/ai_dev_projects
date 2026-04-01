import os
import requests
import json
from dotenv import load_dotenv

# Load config
load_dotenv(r"c:\Users\buyak\Documents\AI_devs\zadania\.config")
apikey = os.getenv("APIKEY")

url = "https://hub.ag3nts.org/verify"

# 1. Update zadania
payload1 = {
    "apikey": apikey,
    "task": "okoeditor",
    "answer": {
        "action": "update",
        "page": "zadania",
        "id": "380792b2c86d9c5be670b3bde48e187b",
        "done": "YES",
        "content": "Widziano bobry"
    }
}
r1 = requests.post(url, json=payload1)
print("Update zadania response:", r1.text)

# 2. Update an incident (Komarowo)
payload2 = {
    "apikey": apikey,
    "task": "okoeditor",
    "answer": {
        "action": "update",
        "page": "incydenty",
        "id": "ff3313a39099222e325f03b378680e3c",
        "title": "Ruch ludzi w okolicach miasta Komarowo",
        "content": "Wykryto ruch ludzi w okolicach miasta Komarowo"
    }
}
r2 = requests.post(url, json=payload2)
print("Update Komarowo incident response:", r2.text)

# 3. Update Skolwin incident
payload3 = {
    "apikey": apikey,
    "task": "okoeditor",
    "answer": {
        "action": "update",
        "page": "incydenty",
        "id": "380792b2c86d9c5be670b3bde48e187b",
        "title": "MOVE03 Trudne do klasyfikacji ruchy nieopodal miasta Skolwin",
        "content": "Zwierzęta, bobry"
    }
}
r3 = requests.post(url, json=payload3)
print("Update Skolwin incident response:", r3.text)

# 4. Action done
payload4 = {
    "apikey": apikey,
    "task": "okoeditor",
    "answer": {
        "action": "done"
    }
}
r4 = requests.post(url, json=payload4)
print("Action done response:", r4.text)
