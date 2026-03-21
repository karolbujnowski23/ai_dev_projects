# Universal Python MCP Server Template

A complete, structured template for creating [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) servers and Agents in Python. Based on best practices extracted from the `@4th-devs-python` projects.

## Project Structure

```text
template-mcp-python/
├── app.py                  # Main entry point (runs the MCP server)
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── workspace/              # Directory for sandbox/file operations
└── src/
    ├── agent.py            # Agent logic placeholder (if acting as a client)
    ├── config.py           # Configuration loading via dotenv
    ├── prompts/            # Centralized storage for skills, prompts, and instructions
    │   └── instructions.py # Static system prompts and templates
    ├── helpers/
    │   └── logger.py       # Stderr logger (CRITICAL for stdio MCP servers)
    └── mcp/
        ├── server.py       # FastMCP server definition (Tools, Resources, Prompts)
        └── client.py       # MCP client connection utility
```

## Getting Started

1. **Setup Environment**:
   ```bash
   python -m venv venv
   source venv/Scripts/activate # Windows
   pip install -r requirements.txt
   cp .env.example .env
   ```

2. **Define Tools**:
   Open `src/mcp/server.py` and modify the `@mcp_server.tool()` decorators. Ensure you provide accurate type hints and docstrings—this is how LLMs understand what your tools do.

3. **Run the Server**:
   ```bash
   python app.py
   ```
   *Note: Running this directly in the terminal will start listening on `stdio`. It will look like it's hanging because it's waiting for JSON-RPC messages from a client.*

## Integration with Claude Desktop

To add this server to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "my-python-server": {
      "command": "python",
      "args": ["C:/absolute/path/to/template-mcp-python/app.py"],
      "env": {
        "LOG_LEVEL": "info"
      }
    }
  }
}
```

## Best Practices (Implemented Here)
- **Logging to Stderr**: Standard `print()` or stdout logging will corrupt the JSON-RPC messages used by MCP. `src/helpers/logger.py` ensures logs go to stderr.
- **FastMCP**: Uses the high-level `FastMCP` class to automatically generate JSON Schema definitions from Python type hints.
- **Modularity**: Tools, Prompts, Config, and Agent logic are clearly separated for scalability.
