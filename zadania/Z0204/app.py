import logging
import os
import json
from src.api import call_gemini, extract_gemini_text, extract_gemini_tool_calls
from src.tools import TOOLS, call_zmail_api, submit_verification

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Orchestrator")

SYSTEM_PROMPT = """You are an AI assistant trying to solve the 'mailbox' task.
You have access to a mailbox of a system operator. Wiktor sent an email from 'proton.me' reporting on us.
You need to find three specific pieces of information:
1. date: when (format YYYY-MM-DD) the security department plans to attack the power plant.
2. password: password to the employee system.
3. confirmation_code: confirmation code from the ticket sent by the security department (format: SEC- + 32 characters = 36 characters total).

IMPORTANT:
1. Use `call_zmail_api` with `action="help"` to see available endpoints/parameters.
2. Search emails using the zmail API. (e.g., action="list", query="...", etc. Read the help first!)
3. Download full email contents to read them, as subjects are not enough.
4. Keep searching iteratively until you have all 3 pieces of information. The mailbox is actively receiving emails! If you can't find something, wait and search again.
5. Once you have all three values, call `submit_verification(date, password, confirmation_code)`.

Be systematic. Start with help, then list/search inbox, then read specific messages.
"""

def execute_tool(name: str, args: dict):
    if name == "call_zmail_api":
        return call_zmail_api(**args)
    elif name == "submit_verification":
        return submit_verification(**args)
    else:
        raise ValueError(f"Unknown tool: {name}")

def run_agent():
    messages = [
        {"role": "user", "parts": [{"text": "Start the task."}]}
    ]

    max_steps = 25
    for step in range(max_steps):
        logger.info(f"--- Step {step+1} ---")
        response = call_gemini(
            messages=messages,
            model="gemini-2.5-flash",
            system_prompt=SYSTEM_PROMPT,
            tools=TOOLS
        )

        text = extract_gemini_text(response)
        if text:
            logger.info(f"Agent says: {text}")
            
        tool_calls = extract_gemini_tool_calls(response)
        
        # Append the model's message (text and/or tool_calls)
        model_parts = []
        if text:
            model_parts.append({"text": text})
        for tc in tool_calls:
            model_parts.append({"functionCall": tc})
            
        if model_parts:
            messages.append({"role": "model", "parts": model_parts})
            
        if not tool_calls:
            logger.info("No tool calls made. Asking agent to continue.")
            messages.append({"role": "user", "parts": [{"text": "Please use tools to gather information and solve the task."}]})
            continue

        # Execute tools and build tool response parts
        tool_responses = []
        for tc in tool_calls:
            name = tc["name"]
            args = tc.get("args", {})
            logger.info(f"Executing tool: {name}({args})")
            
            try:
                result = execute_tool(name, args)
            except Exception as e:
                logger.error(f"Error executing {name}: {e}")
                result = {"error": str(e)}

            tool_responses.append({
                "functionResponse": {
                    "name": name,
                    "response": {"result": result}
                }
            })
            
            if name == "submit_verification":
                logger.info(f"Verification submitted. Result: {result}")
                if "FLG" in str(result) or (isinstance(result, dict) and result.get("code") == 0):
                    logger.info("Task successfully solved!")
                    return
                else:
                    logger.info("Verification failed, continuing search.")
        
        # Append tool responses as 'user'
        messages.append({
            "role": "user",
            "parts": tool_responses
        })

    logger.info("Max steps reached. Exiting.")

if __name__ == "__main__":
    run_agent()
