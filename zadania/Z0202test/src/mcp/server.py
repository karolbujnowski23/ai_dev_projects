import json
from mcp.server.fastmcp import FastMCP
from src.helpers.logger import log
from src.prompts.instructions import SYSTEM_PROMPT, CODE_REVIEW_SKILL, get_summarization_prompt

# Initialize FastMCP Server
mcp_server = FastMCP("template-mcp-server")

@mcp_server.tool()
def sample_action(query: str, limit: int = 5) -> str:
    """
    Perform a sample action based on the query. Replace this with actual tool logic.

    Args:
        query: The search query or command parameter.
        limit: The maximum number of items to return.

    Returns:
        JSON string containing the tool execution result.
    """
    log.info(f"Executing sample_action with query='{query}', limit={limit}")
    
    try:
        # TODO: Implement your tool logic here
        result = {
            "status": "success",
            "data": f"Processed '{query}' with a limit of {limit}"
        }
        return json.dumps(result)
    except Exception as e:
        log.error(f"Error in sample_action: {str(e)}")
        return json.dumps({"status": "error", "message": str(e)})

@mcp_server.resource("config://app-settings")
def get_settings() -> str:
    """
    Exposes application settings as a read-only resource to the LLM.
    """
    log.info("Accessing config resource")
    return json.dumps({
        "environment": "development",
        "version": "1.0.0"
    })

@mcp_server.prompt()
def review_task(context: str) -> str:
    """
    Provide a reusable prompt template for the LLM.
    
    Args:
        context: The context or task description to review.
    """
    return f"{SYSTEM_PROMPT}\n\nTask: {context}\n\n{CODE_REVIEW_SKILL}"

@mcp_server.prompt()
def summarize_text(text: str) -> str:
    """
    A prompt template utilizing the dynamic get_summarization_prompt from instructions.py
    
    Args:
        text: The text to summarize.
    """
    return get_summarization_prompt(text)
