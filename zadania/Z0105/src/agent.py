# -*- coding: utf-8 -*-

import json
import asyncio
from src.api import chat_responses, extract_tool_calls, extract_text
from src.mcp.server import get_help, reconfigure, set_status, save, get_status
from src.helpers.logger import log

MAX_STEPS = 15

TASK_TOOLS = [
    {
        "name": "get_help",
        "description": "Get documentation for the railway API. Start here to learn available actions.",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "reconfigure",
        "description": "Start reconfiguration mode for a specific route (e.g., X-01). Required before setting status.",
        "parameters": {
            "type": "object",
            "properties": {
                "route": {"type": "string", "description": "The route name, e.g., 'X-01'."}
            },
            "required": ["route"]
        }
    },
    {
        "name": "set_status",
        "description": "Set the status for a route while in reconfigure mode.",
        "parameters": {
            "type": "object",
            "properties": {
                "route": {"type": "string", "description": "The route name, e.g., 'X-01'."},
                "value": {"type": "string", "description": "The status value (e.g., 'RTOPEN' for open, 'RTCLOSE' for close)."}
            },
            "required": ["route", "value"]
        }
    },
    {
        "name": "save",
        "description": "Save changes and exit reconfigure mode for a route.",
        "parameters": {
            "type": "object",
            "properties": {
                "route": {"type": "string", "description": "The route name, e.g., 'X-01'."}
            },
            "required": ["route"]
        }
    },
    {
        "name": "get_status",
        "description": "Get the current status of a specific route.",
        "parameters": {
            "type": "object",
            "properties": {
                "route": {"type": "string", "description": "The route name, e.g., 'X-01'."}
            },
            "required": ["route"]
        }
    }
]

TOOL_MAP = {
    "get_help": get_help,
    "reconfigure": reconfigure,
    "set_status": set_status,
    "save": save,
    "get_status": get_status
}

async def run_agent(query: str):
    """Main agent loop."""
    messages = [{"role": "user", "content": query}]
    found_flags = set()
    
    for step in range(MAX_STEPS):
        log.info(f"--- Step {step + 1} ---")
        assistant_message = await chat_responses(messages, tools=TASK_TOOLS)
        
        # Add assistant message to history
        messages.append(assistant_message)
        
        tool_calls = extract_tool_calls(assistant_message)
        final_text = extract_text(assistant_message)
        
        if not tool_calls:
            log.info("Agent finished loop (no tool calls).")
            return final_text
            
        for tool_call in tool_calls:
            name = tool_call["name"]
            args = tool_call.get("arguments", {})
            call_id = tool_call.get("call_id")
            
            log.info(f"🛠️ Tool call: {name}({args})")
            
            if name in TOOL_MAP:
                result = await TOOL_MAP[name](**args)
                
                # Check for errors returned by MCP server
                if isinstance(result, dict) and result.get("error") in ["WAIT_TIME_EXCEEDED", "UNEXPECTED_ERROR", "NETWORK_ERROR"]:
                    log.error(f"❌ Stop: {result['error']}. Reason: {result.get('message', result)}")
                    return f"STOPPED: {result['error']}"

                # Check if we got a flag in the response
                result_str = str(result)
                if "{FLG:" in result_str:
                    # Extract flag(s) using simple regex or split
                    import re
                    flags = re.findall(r"\{FLG:[^}]+\}", result_str)
                    for f in flags:
                        if f not in found_flags:
                            found_flags.add(f)
                            log.box(f"🎯 NEW FLAG FOUND: {f} (Total: {len(found_flags)})")
                    
                    if len(found_flags) >= 2:
                        log.success("✅ Found two flags! Task completed.")
                        return f"SUCCESS: Found flags: {', '.join(found_flags)}"
                
                # Format tool output for the model
                messages.append({
                    "role": "tool",
                    "tool_call_id": call_id,
                    "name": name,
                    "content": json.dumps(result)
                })
            else:
                log.error(f"Unknown tool: {name}")
                messages.append({
                    "role": "tool",
                    "tool_call_id": call_id,
                    "name": name,
                    "content": json.dumps({"error": f"Tool '{name}' not found."})
                })
    
    return "Agent reached maximum steps without finding a flag."
