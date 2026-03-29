import json
import logging
from .api import call_llm

logger = logging.getLogger("Tools")

# 1. TOOL SCHEMAS for Gemini
tools_schemas = [
    {
        "name": "move_left",
        "description": "Moves the transport robot one column to the left. Stays in the bottom row."
    },
    {
        "name": "move_right",
        "description": "Moves the transport robot one column to the right. Stays in the bottom row."
    },
    {
        "name": "wait_tick",
        "description": "The robot stays in its current position, but one tick passes (blocks move)."
    }
]

# 2. SUBAGENT LOGIC
VERIFIER_INSTRUCTIONS = """
**Instruction Name: Reactor Navigation Verifier**

Goal: Validate the Navigator's decision-making process before the command is executed.

Verification Steps:
1. Block Projection: Has the navigator explicitly listed the current position and direction for every block in the path?
2. Boundary Check: If a block is at [1, 2] or [4, 5], has the navigator correctly applied the reversal logic for the next state calculation?
3. Collision Detection: Does the "thought" process specifically verify if Row 5 is occupied (position [4, 5]) in the target column of the chosen command for the upcoming tick?
4. Priority Check: If the navigator chose wait or left, is there a clear explanation of why right was considered unsafe for the next tick?
5. JSON Integrity: Is the output a valid JSON object containing exactly the thought and command keys?

Failure Condition: If any of the above steps are missing or mathematically incorrect (e.g., predicting a block moves from [4, 5] to [5, 6]), reject the response and request a recalculation emphasizing the Reversal Logic.
"""

def verify_system_prompt(system_prompt: str, first_response: dict, model: str = "gemini-2.5-flash"):
    """
    Subagent that verifies the system prompt against the actual API response data.
    """
    logger.info("Running Subagent Prompt Verification...")
    verification_messages = [
        {
            "role": "user", 
            "parts": [{"text": f"System Prompt:\n{system_prompt}\n\nFirst API Response:\n{json.dumps(first_response, indent=2)}"}]
        }
    ]
    verifier_response = call_llm(verification_messages, system_prompt=VERIFIER_INSTRUCTIONS, model=model)
    result = verifier_response.get('content')
    logger.info(f"Subagent Verification Result: {result}")
    return result

def get_tool_command(tool_call: dict) -> str:
    """
    Maps a functionCall name back to a robot command string.
    """
    name = tool_call.get("name")
    if name == "move_left": return "left"
    if name == "move_right": return "right"
    if name == "wait_tick": return "wait"
    return "wait"
