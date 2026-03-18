# -*- coding: utf-8 -*-

#   response.py

import json
from typing import Any, Dict

def parse_json_response(text: str) -> Dict[str, Any]:
    """Parse JSON from AI response, handling markdown blocks."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first and last lines if they are markers
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON", "raw": text}
