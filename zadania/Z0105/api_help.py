from dotenv import load_dotenv
import requests
import os
import json

load_dotenv("../.config")


url = "https://hub.ag3nts.org/verify"
body = {
  "apikey": os.getenv("APIKEY"),
  "task": "railway",
  "answer": {
    "action": "help"
  }
}

help_response = requests.post(url, json=body)
print(help_response.json())

with open("response.json", "w") as f:
    json.dump(help_response.json(), f)   