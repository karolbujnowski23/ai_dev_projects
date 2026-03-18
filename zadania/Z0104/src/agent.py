# -*- coding: utf-8 -*-

import json
import asyncio
from .api import chat_responses, extract_tool_calls, extract_text
from .mcp.server import server
from .native.tools import native_tools
from .helpers.logger import log

MAX_STEPS = 10

# Simplified Tool Definitions for the course's custom format
# Note: The reference project uses a slightly different Tool definition
TASK_TOOLS = [
    {
        "name": "list_docs",
        "description": "List all documentation files available in the docs/ folder.",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "read_doc",
        "description": "Read the content of a specific documentation file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "The name of the file to read."}
            },
            "required": ["filename"]
        }
    },
    {
        "name": "get_image_path",
        "description": "Get the absolute path of an image file for vision analysis.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "The name of the image file."}
            },
            "required": ["filename"]
        }
    },
    {
        "name": "vision_analyze",
        "description": "Analyze an image using a vision model. Provide the absolute path from get_image_path.",
        "parameters": {
            "type": "object",
            "properties": {
                "image_path": {"type": "string", "description": "Absolute path to the image file."},
                "prompt": {"type": "string", "description": "Question or instruction for the vision model."}
            },
            "required": ["image_path", "prompt"]
        }
    },
    {
        "name": "submit_declaration",
        "description": "Submit the final transport declaration for verification.",
        "parameters": {
            "type": "object",
            "properties": {
                "declaration": {"type": "string", "description": "The full text of the declaration."}
            },
            "required": ["declaration"]
        }
    }
]

async def run_agent(query: str):
    """Main agent loop."""
    from .mcp.server import list_docs, read_doc, get_image_path
    from .native.tools import vision_tool, submit_declaration
    
    # Mapping for easy execution
    TOOL_MAP = {
        "list_docs": list_docs,
        "read_doc": read_doc,
        "get_image_path": get_image_path,
        "vision_analyze": vision_tool,
        "submit_declaration": submit_declaration
    }
    
    # Custom format uses 'input' as list of strings/objects
    messages = [{"role": "user", "content": query}]
    
    for _ in range(MAX_STEPS):
        assistant_message = await chat_responses(messages, tools=TASK_TOOLS)
        
        # Add the full assistant message to history (essential for tool_calls meta)
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
            
            log.info(f"Calling tool: {name}({args})")
            
            try:
                if name in TOOL_MAP:
                    result = await TOOL_MAP[name](**args) if asyncio.iscoroutinefunction(TOOL_MAP[name]) else TOOL_MAP[name](**args)
                    log.info(f"Tool {name} result: {str(result)[:100]}...")
                else:
                    result = f"Error: Tool {name} not found."
                    log.error(result)
            except Exception as e:
                result = f"Error executing tool {name}: {str(e)}"
                log.error(result)
                
            # Append tool response matching the call_id
            messages.append({
                "role": "tool",
                "tool_call_id": call_id,
                "name": name,
                "content": str(result)
            })
            
    log.error("Max steps reached.")
    return "Max steps reached without completion."
