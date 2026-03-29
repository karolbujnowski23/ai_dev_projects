import logging
import time
from src.api import call_shell, verify_task

logger = logging.getLogger("Tools")

class ShellTool:
    def __init__(self):
        pass

    def execute_command(self, cmd: str) -> str:
        """
        Execute a shell command in the remote VM.
        """
        logger.info(f"Executing: {cmd}")
        result = call_shell(cmd)
        
        # Handle Rate Limiting
        if result.get("code") == -9999:
            logger.warning("Rate limit hit. Sleeping for 3 seconds...")
            time.sleep(3)
            # Retry once after sleep
            result = call_shell(cmd)
            
        # Handle Active Ban
        if result.get("code") in [-733, -735]:
            ban_info = result.get("ban", {})
            seconds_left = ban_info.get("ttl_seconds", ban_info.get("seconds_left", 15))
            logger.warning(f"Banned! Sleeping for {seconds_left + 1} seconds to recover...")
            time.sleep(seconds_left + 1)
            return "You were temporarily banned but the ban has now expired. You may proceed."

        # Sleep for a baseline 1.5 seconds to avoid rate limits on normal operations
        time.sleep(1.5)

        # Return the raw dictionary as a string so the LLM can see data, path, code, and message
        import json
        return json.dumps(result)

    def submit_code(self, code: str) -> str:
        """
        Submit the final ECCS code to verify the task.
        """
        logger.info(f"Submitting final code: {code}")
        result = verify_task(code)
        return str(result)

shell_tool_instance = ShellTool()

tool_mapping = {
    "execute_command": shell_tool_instance.execute_command,
    "submit_code": shell_tool_instance.submit_code
}

tools_schemas = [
    {
        "type": "function",
        "function": {
            "name": "execute_command",
            "description": "Execute a shell command in the remote VM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cmd": {
                        "type": "string",
                        "description": "The shell command to execute."
                    }
                },
                "required": ["cmd"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "submit_code",
            "description": "Submit the final ECCS code to verify the task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The obtained code, format: ECCS-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                    }
                },
                "required": ["code"]
            }
        }
    }
]
