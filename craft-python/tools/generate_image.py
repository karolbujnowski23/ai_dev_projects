import os
import requests
import time
import base64

OUTPUT_DIR = os.path.abspath("output")

definition = {
    "type": "function",
    "name": "generate_image",
    "description": "Generates an image from a text prompt using Gemini Nano Banana 2 and saves it to disk",
    "strict": False,
    "parameters": {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "Text description of the image to generate",
            },
        },
        "required": ["prompt"],
        "additionalProperties": False,
    },
}

def execute(args):
    prompt = args.get("prompt")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": os.getenv("GEMINI_API_KEY", ""),
    }
    payload = {
        "model": "gemini-3.1-flash-image-preview",
        "input": prompt,
        "response_modalities": ["IMAGE"],
    }
    
    response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/interactions",
        headers=headers,
        json=payload
    )
    
    if not response.ok:
        raise Exception(f"Gemini API error ({response.status_code}): {response.text}")
        
    data = response.json()
    outputs = data.get("outputs", [])
    image = next((o for o in outputs if o.get("type") == "image"), None)
    
    if not image:
        raise Exception("No image returned from Gemini API")
        
    filename = f"image_{int(time.time() * 1000)}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, "wb") as f:
        f.write(base64.b64decode(image.get("data", "")))
        
    return {"filepath": filepath, "filename": filename}