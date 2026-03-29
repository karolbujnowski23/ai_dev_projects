import logging
import os
import json
from src.api import call_llm, call_verify
from src.tools import tools_schemas, verify_system_prompt, get_tool_command
from src.config import TASK_NAME

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Orchestrator")

# Load System Prompt
PROMPT_PATH = os.path.join(os.path.dirname(__file__), "src", "reactor_navigator_return.prompt.md")
with open(PROMPT_PATH, "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

def main():
    logger.info("Mission start: REACTOR NAVIGATION (There and Back Again)")
    
    # Initialize mission
    initial_response = call_verify("start")
    
    if "error" in initial_response:
        logger.error(f"Failed to start mission: {initial_response}")
        return

    messages = []
    
    # Add initial mission data to history
    messages.append({
        "role": "user",
        "parts": [{"text": f"Current map state: {json.dumps(initial_response, indent=2)}\n\nMission Phase: TO_GOAL"}]
    })

    max_steps = 50
    model = "gemini-2.5-flash"
    mission_phase = "TO_GOAL" # 'TO_GOAL' or 'TO_START'
    flags_found = []

    for step in range(max_steps):
        logger.info(f"--- Step {step+1} --- Mission Phase: {mission_phase} ---")
        
        # Call LLM to decide next move with TOOLS
        response_msg = call_llm(messages, system_prompt=SYSTEM_PROMPT, model=model, tools=tools_schemas)
        
        thought = response_msg.get("content", "")
        if thought:
            logger.info(f"Thought: {thought}")
            
        command = "wait" # default
        if "tool_calls" in response_msg and response_msg["tool_calls"]:
            tc = response_msg["tool_calls"][0]
            command = get_tool_command(tc)
            logger.info(f"Tool decision: {tc['name']} -> {command}")
        else:
            logger.warning("No tool call in model response. Falling back to text search.")
            if "left" in thought.lower() and mission_phase == "TO_START":
                command = "left"
            elif "right" in thought.lower() and mission_phase == "TO_GOAL":
                command = "right"
            else: # Default to wait on uncertainty
                command = "wait"

        logger.info(f"Command to API: {command}")
        
        # Execute command
        result = call_verify(command)
        
        # Log result
        logger.info(f"API Response: {result}")
        
        # Check for flags and completion
        res_str = json.dumps(result)
        if "FLG:" in res_str.upper():
            if res_str not in flags_found:
                logger.info(f"Found new flag: {res_str}")
                flags_found.append(res_str)

        # State transition logic
        current_col = result.get('player', {}).get('col')
        if mission_phase == "TO_GOAL" and current_col == 7:
            logger.info("Goal reached! Switching mission phase to TO_START.")
            mission_phase = "TO_START"
            messages.append(response_msg)
            messages.append({
                "role": "user",
                "parts": [{"text": f"Goal reached. API Response: {res_str}. Phase 2 begins now: Return to the start at Column 1. Prioritize `move_left`."}]
            })
            continue

        # Termination condition
        if mission_phase == "TO_START" and current_col == 1 and len(flags_found) > 1:
            logger.info(f"Returned to start position with all flags. Mission complete! Flags: {flags_found}")
            break
            
        is_dict = isinstance(result, dict)
        if (is_dict and "error" in result) or "Game over" in res_str or (is_dict and result.get("message") == 'Robot was crushed :('):
            logger.error(f"Mission failed: {result}")
            break

        # Append model and user turns to history atomically
        messages.append(response_msg) 
        
        user_response_parts = []
        if "tool_calls" in response_msg and response_msg["tool_calls"]:
            for tc in response_msg["tool_calls"]:
                user_response_parts.append({
                    "functionResponse": {
                        "name": tc["name"],
                        "response": {"result": json.dumps(result)}
                    }
                })
        else:
             user_response_parts.append({"text": f"API response: {json.dumps(result)}"})
        
        # Add phase transition instructions if needed
        if mission_phase == "TO_START" and current_col == 7: # This condition was wrong before
            user_response_parts.append({"text": "You have reached the goal. Phase 2 begins now: Return to the start at Column 1. Prioritize `move_left`."})

        messages.append({
            "role": "user",
            "parts": user_response_parts
        })
        
        # Limit history size
        if len(messages) > 12:
            messages = messages[-12:]

    logger.info("Loop ended.")

if __name__ == "__main__":
    main()
