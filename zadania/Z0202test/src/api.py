import os
import json
import base64
import requests
from dotenv import load_dotenv
load_dotenv("C:/Users/buyak/Documents/AI_devs/zadania/.config")

GEMINI_API_KEY = os.getenv("GEMINI_LLM_APIKEY")
API_URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
APIKEY = os.getenv("APIKEY")

def analyze_board_image(image_path: str) -> str:
    """
    Analizuje obraz planszy używając modelu Gemini i zwraca listę pól.
    Wykorzystuje model gemini-3-flash-preview.
    """
    if not GEMINI_API_KEY:
        raise ValueError("Brak klucza GEMINI_API_KEY w zmiennych środowiskowych.")

    # Ustalanie typu MIME na podstawie rozszerzenia
    mime_type = "image/jpeg"
    ext = image_path.lower().split('.')[-1]
    if ext == "png":
        mime_type = "image/png"
    elif ext == "webp":
        mime_type = "image/webp"

    if image_path.startswith("http://") or image_path.startswith("https://"):
        img_resp = requests.get(image_path)
        img_resp.raise_for_status()
        image_data = img_resp.content
    else:
        with open(image_path, "rb") as f:
            image_data = f.read()
    
    encoded_image = base64.b64encode(image_data).decode("utf-8")

    prompt = """zwróć uwagęjedynie na znajdujący sie na środku kwadrat przypominający szachownicę - trzy pola na trzy pola,  składającą sie z 9 elementów. 
przeanalizuj dokładnie kazdy element tej szachownicy w celu określenia kształtu elementu który sie na nim znajduje. Do nazwania kształtów znajdujących się na grafice uzyj liter arfabetu L T I oraz kątów o jaki są obrucone względem osi pionowej. 
Wartość kąta o jaki obrócona jest litera mierzona jest zgodnie z ruchem wskazówek zegara - czyli w prawo.
Możesz użyć kątów 0° (nieobrócony), 90° (obrócony w prawo), 180° (obrócony do góry nogami - obrócony dwa razy w prawo) i 270° (obrócony trzy razy w prawo).
Do identyfikacji pól uzyj nastepującego schematu:
```
1x1 | 1x2 | 1x3
----|-----|----
2x1 | 2x2 | 2x3
----|-----|----
3x1 | 3x2 | 3x3
```
w odpowiedzi zwróć listę elementów macieży wraz z przypisanym symbolem i kątem. Nie dodawaj opisu. zwroc sama liste 
oczekiwany format:
1x1: symbol L, kąt °
1x2: symbol T, kąt ° 
1x3: symbol I, kąt ° 
2x1: symbol I, kąt ° 
2x2: symbol T, kąt ° 
2x3: symbol T, kąt ° 
3x1: symbol T, kąt ° 
3x2: symbol L, kąt ° 
3x3: symbol L, kąt ° 

"""

    url = API_URL_BASE.format(model="gemini-3-flash-preview")
    
    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [{
            "parts": [
                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": encoded_image
                    }
                },
                {"text": prompt}
            ]
        }]
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    
    data = response.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        return ""


def compare_board_states(target_state: str, current_state: str) -> str:
    """
    Porównuje dwa stany planszy używając modelu Gemini 2.5 Flash i oblicza ilość 
    obrotów o 90 stopni w lewo dla każdego elementu z listy stan bieżący, 
    aby uzyskać stan docelowy.
    """
    if not GEMINI_API_KEY:
        raise ValueError("Brak klucza GEMINI_API_KEY w zmiennych środowiskowych.")

    prompt = f"""Porównaj ze sobą dwie listy reprezentujące stan pól na szachownicy składającej sie z 9 elementów.
Twoim zadaniem jest policzenie ile obrotów o 90 stopni w prawo powinien wykonać każdy element z listy 'Stan bieżący', aby uzyskać dokładnie taki sam symbol i kąt jak na odpowiadającym polu w liście 'Stan docelowy'.
Pamiętaj ze w przypadku literu I nie ma znaczenia czy jest obrócona o 90 czy 270 stopni, w obu przypadkach jest to ten sam symbol i kąt.
Jesli jakaś litera z listy 'Stan bieżący' ten sam kąt odpowiadająca jej litera z listy 'Stan docelowy' to liczba obrotów dla tego pola wynosi 0
Teśli litera T jest obrócona o 90 stopni w prawo w 'Stanie bieżącym' a w 'Stanie docelowym' jest obrócona o 180 stopni to liczba obrotów dla tego pola wynosi 1
{target_state}

Lista 2 (Stan bieżący):
{current_state}

Zwróć wynik w przejrzystej formie, dla każdego pola np:
1x1: 1 (obrót)
1x2: 0 (obrótów)
...
nie pisz słowa 'obrót', 'obrotów', 'obroty', po prostu LICZBĘ obrotów.
Nie dodawaj żadnych innych wyjaśnień, podaj tylko listę z numerami pól i ilością wymaganych obrotów o 90 stopni w prawo.
"""

    url = API_URL_BASE.format(model="gemini-2.5-flash")
    
    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [{
            "parts": [
                {"text": prompt}
            ]
        }]
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    
    data = response.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        return ""

if __name__ == "__main__":

    # Test (wymaga odpowiedniego środowiska i obrazu)
    # print(analyze_board_image("image.jpg"))

    stan_docelowy_img= "https://hub.ag3nts.org/i/solved_electricity.png"
    stan_początkowy_img = f"https://hub.ag3nts.org/data/{APIKEY}/electricity.png"
    stan_docelowy_result = analyze_board_image(stan_docelowy_img)
    stan_początkowy_result = analyze_board_image(stan_początkowy_img)
    print("Stan docelowy:") 
    print(stan_docelowy_result)
    print("Stan początkowy:") 
    print(stan_początkowy_result)
    rotations = compare_board_states(stan_docelowy_result, stan_początkowy_result)
    print("Obroty do wykonania:")       
    print(rotations)    
    pass
