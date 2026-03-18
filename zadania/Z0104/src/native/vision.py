# -*- coding: utf-8 -*-

import base64
import hashlib
import httpx
from typing import Optional
from ..config import LLM_API_KEY, API_CONFIG
from ..helpers.cache import get_cache_key, get_from_cache, save_to_cache
from ..helpers.logger import log

async def analyze_image(image_path: str, prompt: str, model: Optional[str] = None) -> str:
    """Analyze an image using vision model via OpenRouter, with caching."""
    _model = model or API_CONFIG["vision_model"]
    
    # Create cache key based on file content and prompt
    with open(image_path, "rb") as f:
        img_bytes = f.read()
        image_data = base64.b64encode(img_bytes).decode("utf-8")
        
    cache_key = get_cache_key({"image_md5": hashlib.md5(img_bytes).hexdigest(), "prompt": prompt, "model": _model})
    cached_result = get_from_cache(cache_key)
    
    if cached_result:
        log.info(f"Using cached vision results for {image_path.split('/')[-1]}")
        return cached_result["content"]

    mime_type = "image/png" if image_path.endswith(".png") else "image/jpeg"
    
    log.info(f"Calling vision API for {image_path.split('/')[-1]}...")
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {LLM_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/mcp/python-sdk", # Optional
            "X-Title": "Z0104 Vision Agent", # Optional
        },
# ...existing code...
        json={
            "model": _model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_data}"
                            }
                        }
                    ]
                }
            ]
        }
    )
    
    if response.status_code != 200:
        return f"Error: API returned {response.status_code} - {response.text}"
        
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    
    # Save to cache
    save_to_cache(cache_key, {"content": content})
    
    return content
