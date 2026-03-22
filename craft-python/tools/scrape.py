import os
import requests

BASE_URL = "https://api.firecrawl.dev/v2"

definition = {
    "type": "function",
    "name": "scrape_url",
    "description": "Scrapes a single URL and returns its content as markdown",
    "strict": False,
    "parameters": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The URL to scrape",
            },
        },
        "required": ["url"],
        "additionalProperties": False,
    },
}

def execute(args):
    url = args.get("url")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('FIRECRAWL_API_KEY')}",
    }
    payload = {
        "url": url,
        "formats": [{"type": "markdown"}]
    }
    
    response = requests.post(f"{BASE_URL}/scrape", headers=headers, json=payload)
    if not response.ok:
        raise Exception(f"Firecrawl scrape error ({response.status_code}): {response.text}")
        
    data = response.json().get("data", {})
    metadata = data.get("metadata", {})
    
    return {
        "url": metadata.get("url", url),
        "title": metadata.get("title"),
        "description": metadata.get("description"),
        "markdown": data.get("markdown")
    }