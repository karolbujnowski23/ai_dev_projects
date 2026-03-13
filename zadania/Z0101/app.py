import requests

# Set API endpoint and headers
url = "https://hub.ag3nts.org/verify"
headers = {"Content-Type": "application/json"}

# Define request body
data = {
  "apikey": "aef1bda3-8909-428e-986e-1042b1a197c7",
  "task": "people",
  "answer": [
    {
      "name": "Cezary",
      "surname": "Żurek",
      "gender": "M",
      "born": 1987,
      "city": "Grudziądz",
      "tags": ["transport"]
    },
    {
      "name": "Jacek",
      "surname": "Nowak",
      "gender": "M",
      "born": 1991,
      "city": "Grudziądz",
      "tags": ["transport"]
    },
    {
      "name": "Oskar",
      "surname": "Sieradzki",
      "gender": "M",
      "born": 1993,
      "city": "Grudziądz",
      "tags": ["transport"]
    },
    {
      "name": "Wojciech",
      "surname": "Bielik",
      "gender": "M",
      "born": 1986,
      "city": "Grudziądz",
      "tags": ["transport"]
    },
    {
      "name": "Wacław",
      "surname": "Jasiński",
      "gender": "M",
      "born": 1986,
      "city": "Grudziądz",
      "tags": ["transport"]
    }
  ]
}
# Make POST request
response = requests.post(url, json=data, headers=headers)

# Handle response
if response.status_code == 200:
    print("Success:", response.json())
else:
    print("Error:", response.status_code, response.text)