import requests
import re
from src.config import APIKEY

s = requests.Session()
s.post("https://oko.ag3nts.org/", data={"action": "login", "login": "Zofia", "password": "Zofia2026!", "access_key": APIKEY})
html = s.get("https://oko.ag3nts.org/").text
blocks = re.findall(r'<article class="list-item[^>]*>.*?</article>', html, re.DOTALL)
for b in blocks:
    if "Skolwin" in b:
        print("INCIDENT SKOLWIN:\n", b)

html2 = s.get("https://oko.ag3nts.org/zadania").text
blocks2 = re.findall(r'<article class="list-item[^>]*>.*?</article>', html2, re.DOTALL)
for b in blocks2:
    if "Skolwin" in b:
        print("ZADANIE SKOLWIN:\n", b)
