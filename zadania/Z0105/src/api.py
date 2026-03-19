# -*- coding: utf-8 -*-

import httpx
import json
from typing import Any, Dict, List, Optional
from src.config import LLM_API_KEY, API_CONFIG
from src.helpers.logger import log

async def chat_responses(input_messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Call OpenRouter's chat/completions API using standard messages array.
    """
    
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/mcp/python-sdk",
        "X-Title": "AI_devs_examples"
    }

    # Prepare standard OpenAI-compatible messages including system instructions
    messages = [{"role": "system", "content": API_CONFIG["instructions"]}] + input_messages
    
    body = {
        "model": API_CONFIG["model"],
        "messages": messages,
        "max_tokens": API_CONFIG.get("max_output_tokens", 4096)
    }
    
    if tools:
        # Convert tools to standard OpenAI format
        body["tools"] = [{"type": "function", "function": t} for t in tools]
        body["tool_choice"] = "auto"

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=body
        )
        
        if response.status_code != 200:
            raise Exception(f"API error: {response.status_code} - {response.text}")
            
        data = response.json()
        
        if "choices" in data:
            message = data["choices"][0]["message"]
            return message
            
        return data

def extract_tool_calls(message: dict) -> list:
    """Extract tool calls from a standard OpenAI message object."""
    if not isinstance(message, dict):
        return []
    
    tool_calls = message.get("tool_calls", [])
    if not tool_calls:
        return []
        
    return [
        {
            "type": "function_call",
            "name": tc["function"]["name"],
            "arguments": json.loads(tc["function"]["arguments"]),
            "call_id": tc["id"]
        }
        for tc in tool_calls
    ]

def extract_text(message: dict) -> Optional[str]:
    """Extract text content from a standard OpenAI message object."""
    if not isinstance(message, dict):
        return None
    return message.get("content")
