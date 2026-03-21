from src.helpers.logger import log

TASK_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_board_state",
            "description": "Download the PNG image of the current board and analyze the arrangement of cables on all 9 fields.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_boards",
            "description": "Compare the current board state with the target board state to determine which fields need rotation and how many 90-degree right rotations each field requires.",
            "parameters": {
                "type": "object",
                "properties": {
                    "current_state": {
                        "type": "string",
                        "description": "The description or layout of the current board."
                    },
                    "target_state": {
                        "type": "string",
                        "description": "The description or layout of the target board."
                    }
                },
                "required": ["current_state", "target_state"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rotate_fields",
            "description": "Send the required number of rotations (90 degrees right) for specific fields via API.",
            "parameters": {
                "type": "object",
                "properties": {
                    "rotations": {
                        "type": "array",
                        "description": "List of fields to rotate and the number of rotations.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "field": {
                                    "type": "string",
                                    "description": "The address of the field (e.g., '1x1', '3x2')."
                                },
                                "count": {
                                    "type": "integer",
                                    "description": "Number of 90-degree right rotations."
                                }
                            },
                            "required": ["field", "count"]
                        }
                    }
                },
                "required": ["rotations"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "verify_result",
            "description": "Download the updated PNG image and verify if the board matches the target schema. Retrieves the flag if the configuration is correct.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

async def get_board_state():
    """Implementation for getting the board state"""
    log.info("Executing get_board_state")
    pass

async def compare_boards(current_state: str, target_state: str):
    """Implementation for comparing boards"""
    log.info(f"Executing compare_boards")
    pass

async def rotate_fields(rotations: list):
    """Implementation for rotating fields"""
    log.info(f"Executing rotate_fields with {len(rotations)} rotations")
    pass

async def verify_result():
    """Implementation for verifying the result"""
    log.info("Executing verify_result")
    pass

TOOL_MAP = {
    "get_board_state": get_board_state,
    "compare_boards": compare_boards,
    "rotate_fields": rotate_fields,
    "verify_result": verify_result
}

class Agent:
    def __init__(self, name: str = "TemplateAgent"):
        self.name = name

    async def run(self, task: str):
        """
        Main execution loop for the agent.
        Integrate LLM calls and tool execution here.
        """
        log.info(f"[{self.name}] Starting task: {task}")
        # TODO: Implement agentic loop (e.g., Anthropic API / OpenAI API calling MCP tools)
        pass
