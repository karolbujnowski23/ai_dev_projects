import json
import base64
import requests
from io import BytesIO
from PIL import Image
from src.config import GEMINI_API_KEY

API_URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

VISION_PROMPT = """
Na obrazku znajduje się jeden fragment planszy (kafelek) z namalowanym przewodem.
Twoim zadaniem jest sprawdzenie, do jakich krawędzi tego kafelka dochodzi przewód.
Krawędzie to tylko i wyłącznie: "top" (góra), "bottom" (dół), "left" (lewo), "right" (prawo).

Zwróć TYLKO wynik w postaci poprawnego JSON, bez absolutnie żadnego innego tekstu, bez znaczników markdown (np. ```json):
{
  "edges": ["top", "left"]
}
Jeśli przewodu nie ma lub nie dotyka żadnej z krawędzi, zwróć "edges": []
"""

def get_edges(image_data):
    encoded_image = base64.b64encode(image_data).decode("utf-8")
    
    url = API_URL_BASE.format(model="gemini-2.5-flash")
    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [{
            "parts": [
                {
                    "inline_data": {
                        "mime_type": "image/png",
                        "data": encoded_image
                    }
                },
                {"text": VISION_PROMPT}
            ]
        }]
    }

    response = requests.post(url, headers=headers, json=payload)
    if not response.ok:
        print(response.text)
    
    data = response.json()
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        if text.startswith("```json"): text = text[7:]
        if text.endswith("```"): text = text[:-3]
        return json.loads(text.strip())["edges"]
    except Exception as e:
        print("Error:", e, data)
        return []

def main():
    img = Image.open('solved.png').convert('RGB')
    
    # 3x3 grid
    width, height = img.size
    print(f"Size: {width}x{height}")
    
    tile_w = width // 3
    tile_h = height // 3
    
    ground_truth = {}
    for row in range(3):
        for col in range(3):
            left = col * tile_w
            top = row * tile_h
            right = left + tile_w
            bottom = top + tile_h
            
            tile = img.crop((left, top, right, bottom))
            buffered = BytesIO()
            tile.save(buffered, format="PNG")
            img_byte = buffered.getvalue()
            
            edges = get_edges(img_byte)
            edges.sort()
            
            tile_id = f"{row+1}x{col+1}"
            ground_truth[tile_id] = edges
            print(f"{tile_id}: {edges}")
            
    print("GROUND TRUTH JSON:")
    print(json.dumps(ground_truth, indent=2))

if __name__ == "__main__":
    main()
