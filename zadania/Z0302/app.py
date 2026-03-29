import logging
import os
import json
from src.api import call_llm
from src.tools import tools_schemas, tool_mapping

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

# Load System Prompt from firmware-solver.prompt.md
PROMPT_PATH = os.path.join(os.path.dirname(__file__), "src", "firmware-solver.prompt.md")
with open(PROMPT_PATH, "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

def main():
    messages = [
        {"role": "user", "content": "Mission start. Call 'help' to begin."}
    ]
    
    max_steps = 50
    model = "anthropic/claude-sonnet-4.6"
    
    for step in range(max_steps):
        logger.info(f"--- Step {step+1} ---")
        
        response_msg = call_llm(messages, system_prompt=SYSTEM_PROMPT, model=model, tools=tools_schemas)
        
        messages.append(response_msg)
        
        if "tool_calls" in response_msg and response_msg["tool_calls"]:
            for tool_call in response_msg["tool_calls"]:
                function_name = tool_call["function"]["name"]
                args_str = tool_call["function"].get("arguments", "{}")
                try:
                    args = json.loads(args_str)
                except:
                    args = {}
                logger.info(f"Tool call: {function_name}({args})")
                
                if function_name in tool_mapping:
                    func = tool_mapping[function_name]
                    result = func(**args)
                    logger.info(f"Result: {result}")
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": function_name,
                        "content": str(result)
                    })
                    
                    if function_name == "submit_code":
                        return # Exit after submitting
        else:
            content = response_msg.get("content", "")
            logger.info(f"Assistant: {content}")
            
            messages.append({
                "role": "user",
                "content": "Please continue investigating using the execute_command tool, or submit the final code if you found it."
            })
            
    logger.warning("Max steps reached without finding the code.")

if __name__ == "__main__":
    main()
