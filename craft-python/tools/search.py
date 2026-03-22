import os
import requests

BASE_URL = "https://api.firecrawl.dev/v2"

definition = {
    "type": "function",
    "name": "web_search",
    "description": "Searches the web for a given query and returns results with markdown content",
    "strict": False,
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query (supports operators like site:, filetype:, intitle:)",
            },
            "limit": {
                "type": "number",
                "description": "Maximum number of results to return (1-100, default 5)",
            },
        },
        "required": ["query"],
        "additionalProperties": False,
    },
}

def execute(args):
    query = args.get("query")
    limit = args.get("limit", 5)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('FIRECRAWL_API_KEY')}",
    }
    payload = {
        "query": query,
        "limit": limit,
        "scrapeOptions": {
            "formats": [{"type": "markdown"}]
        }
    }
    
    response = requests.post(f"{BASE_URL}/search", headers=headers, json=payload)
    if not response.ok:
        raise Exception(f"Firecrawl search error ({response.status_code}): {response.text}")
        
    data = response.json().get("data", {})
    web_results = data.get("web", [])
    
    return [
        {
            "title": res.get("title"),
            "url": res.get("url"),
            "description": res.get("description"),
            "markdown": res.get("markdown")
        }
        for res in web_results
    ]