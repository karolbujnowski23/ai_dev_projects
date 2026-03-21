import asyncio
from typing import AsyncIterator
from mcp import ClientSession
from mcp.server.fastmcp import FastMCP
from src.helpers.logger import log

# Placeholder for creating an in-memory client if you need an Agent talking to MCP within the same process.
async def create_mcp_client(server: FastMCP) -> AsyncIterator[ClientSession]:
    """
    Creates an in-memory MCP client session for a given FastMCP server.
    This is useful for native agent loops (like in 01_03_mcp_native).
    """
    log.info(f"Creating in-memory client for server: {server.name}")
    from mcp.client.session import ClientSession
    from mcp.client.stdio import stdio_client
    
    # Normally for in-memory, you'd use memory transport.
    # For a real standalone server, you connect to external servers via stdio_client.
    pass
