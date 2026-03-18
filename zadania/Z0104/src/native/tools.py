# -*- coding: utf-8 -*-

import httpx
from typing import Any, Dict
from .vision import analyze_image
from ..config import API_KEY, LLM_API_KEY, API_CONFIG

async def vision_tool(image_path: str, prompt: str) -> str:
    """Analyze an image using a vision model.
    
    Args:
        image_path: Absolute path to the image file.
        prompt: Question/prompt to send with the image.
    """
    return await analyze_image(image_path, prompt)

# NOTE: comment out the actual API submission code when NOT ready to test with the Central Hub.
async def submit_declaration(declaration: str) -> str:
    """Submit the transport declaration to the Central Hub for verification.
    
    Args:
        declaration: Full text of the transport declaration.
    """
    url = "https://hub.ag3nts.org/verify"
    payload = {
        "apikey": API_KEY,
        "task": "sendit",
        "answer": {
            "declaration": declaration
        }
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)
        
        if response.status_code != 200:
            return f"Error: {response.status_code} - {response.text}"
            
        return response.text

# NOTE: The submit_declaration function is currently in dry-run mode for testing purposes. It prints the declaration to the console instead of sending it to the API. Uncomment the above code and comment out the below version to enable actual API submission.
# async def submit_declaration(declaration: str) -> str:
#     """DRY RUN - Wypisuje deklarację w konsoli zamiast wysyłać."""
#     print("\n" + "="*20 + " TESTOWA DEKLARACJA " + "="*20)
#     print(declaration)
#     print("="*60 + "\n")
    
#     return "TEST_SUCCESS: Deklaracja wyświetlona w konsoli (tryb dry-run)."

native_tools = [
    {
        "name": "vision_analyze",
        "handler": vision_tool,
        "description": "Analyze an image (like a map or chart) using a vision model."
    },
    {
        "name": "submit_declaration",
        "handler": submit_declaration,
        "description": "Submit the completed transport declaration for verification."
    }
]
