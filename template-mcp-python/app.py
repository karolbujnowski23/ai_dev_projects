from src.mcp.server import mcp_server
from src.helpers.logger import log

def main():
    """
    Entry point for the MCP Server.
    Runs the FastMCP server on stdio.
    """
    log.info("Starting Universal MCP Server Template...")
    mcp_server.run()

if __name__ == "__main__":
    main()
