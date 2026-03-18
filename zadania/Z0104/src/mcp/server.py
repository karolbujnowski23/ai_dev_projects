# -*- coding: utf-8 -*-

#   server.py

import os
from pathlib import Path
from mcp.server import Server
from mcp.types import Tool, TextContent, CallToolResult
from ..config import DOCS_DIR

server = Server("spk-mcp-server")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available documentation files in the SPK system."""
    return [
        Tool(
            name="list_docs",
            description="List all available documentation files (markdown and images).",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="read_doc",
            description="Read a text-based documentation file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "The name of the markdown file to read."}
                },
                "required": ["filename"]
            }
        ),
        Tool(
            name="get_image_path",
            description="Get the absolute path to an image file for vision analysis.",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "The name of the image file (e.g., .png)."}
                },
                "required": ["filename"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> CallToolResult:
    if name == "list_docs":
        files = [f.name for f in DOCS_DIR.iterdir() if f.is_file()]
        return CallToolResult(content=[TextContent(type="text", text="\n".join(files))])
    
    elif name == "read_doc":
        filename = arguments.get("filename")
        file_path = DOCS_DIR / filename
        if not file_path.exists():
            return CallToolResult(content=[TextContent(type="text", text=f"Error: {filename} not found.")], isError=True)
        with open(file_path, "r", encoding="utf-8") as f:
            return CallToolResult(content=[TextContent(type="text", text=f.read())])
            
    elif name == "get_image_path":
        filename = arguments.get("filename")
        file_path = DOCS_DIR / filename
        if not file_path.exists():
            return CallToolResult(content=[TextContent(type="text", text=f"Error: {filename} not found.")], isError=True)
        return CallToolResult(content=[TextContent(type="text", text=str(file_path.absolute()))])
        
    return CallToolResult(content=[TextContent(type="text", text=f"Unknown tool: {name}")], isError=True)

# Helper functions for internal use (agent can import these if it's running in same process)
def list_docs():
    return [f.name for f in DOCS_DIR.iterdir() if f.is_file()]

def read_doc(filename: str):
    file_path = DOCS_DIR / filename
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def get_image_path(filename: str):
    return str((DOCS_DIR / filename).absolute())
