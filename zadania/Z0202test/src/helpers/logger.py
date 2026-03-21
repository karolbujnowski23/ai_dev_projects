import logging
import sys
from src.config import LOG_LEVEL

_LOG_LEVEL_MAP = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
}

# IMPORTANT: MCP Servers communicate via stdio (stdout/stdin).
# All logs MUST go to stderr to avoid corrupting the JSON-RPC messages.
logging.basicConfig(
    level=_LOG_LEVEL_MAP.get(LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)

log = logging.getLogger("mcp-template")
