import logging
import os
import json
from src.api import call_gemini, extract_gemini_tool_calls, extract_gemini_text
from src.tools import TOOLS, execute_tool
from src.scraper import get_oko_data # Import the new scraper

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

MODEL_CONFIG = {
    "executor": {"provider": "gemini", "model": "gemini-3.1-pro-preview"},
}

def main():
    logger.info("Starting Z0401 OKO Editor Agent...")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Get scraped data dynamically
    try:
        oko_data = get_oko_data()
        scraped_data_content = """
=== DANE ZEBRANE Z PORTALU WEB ===
INCIDENTS:
{}

TASKS:
{}
==================================
""".format(
            json.dumps(oko_data["incident_details"], indent=2, ensure_ascii=False),
            json.dumps(oko_data["task_details"], indent=2, ensure_ascii=False)
        )

        # Save for debugging/visibility, but not strictly necessary for prompt injection
        with open(os.path.join(current_dir, "scraped_data.txt"), "w", encoding="utf-8") as f:
            f.write(scraped_data_content)
            
        skolwin_incident_id = oko_data["skolwin_incident_id"]
        skolwin_task_id = oko_data["skolwin_task_id"]
        komarowo_incident_id = oko_data["komarowo_incident_id"]

    except Exception as e:
        logger.error(f"Error during data scraping or processing: {e}")
        return

    # Load system prompt
    try:
        with open(os.path.join(current_dir, "oko_systemprompt.md"), "r", encoding="utf-8") as f:
            system_prompt_template = f.read()
    except FileNotFoundError:
        logger.error("oko_systemprompt.md not found!")
        return

    system_prompt = system_prompt_template.replace("{scraped_data}", scraped_data_content)
    system_prompt = system_prompt.replace("{skolwin_incident_id}", skolwin_incident_id)
    system_prompt = system_prompt.replace("{skolwin_task_id}", skolwin_task_id)
    system_prompt = system_prompt.replace("{komarowo_incident_id}", komarowo_incident_id)
    
    messages = [
        {"role": "user", "parts": [{"text": "Begin the operation by calling the help action."}]}
    ]
    nIterations = 10
    for step in range(nIterations): # Max 15 turns
        logger.info(f"--- Turn {step + 1} ---")
        
        response = call_gemini(
            messages=messages,
            model=MODEL_CONFIG["executor"]["model"],
            system_prompt=system_prompt,
            tools=TOOLS
        )
        
        tool_calls = extract_gemini_tool_calls(response)
        text_response = extract_gemini_text(response)
        
        # Append the model's full response content to maintain conversation history
        try:
            model_content = response["candidates"][0]["content"]
            messages.append(model_content)
        except (KeyError, IndexError):
            logger.error("Failed to get model content from response.")
            break
        
        if text_response:
            logger.info(f"Agent: {text_response}")
            
        if not tool_calls:
            logger.info("No more tool calls. Agent is done.")
            break
            
        tool_parts = []
        for tc in tool_calls:
            name = tc["name"]
            # Gemini provides args as a dict
            args = tc.get("args", {})
            logger.info(f"Tool call: {name} | args: {args}")
            
            # Check for 'done' action and break loop if called
            try:
                payload = json.loads(args.get("action_payload", "{}"))
                if payload.get("action") == "done":
                    logger.info("'done' action detected. Attempting to finalize...")
                    execute_tool(name, args) # Execute the 'done' call
                    logger.info("Agent has completed all tasks and sent 'done'. Terminating.")
                    return # Exit main function
            except (json.JSONDecodeError, AttributeError):
                pass # Not a valid json or structure, continue

            try:
                result_str = execute_tool(name, args)
                # Convert string back to dict for Gemini's functionResponse
                result_dict = json.loads(result_str)
            except Exception as e:
                logger.error(f"Error handling tool call: {e}")
                result_dict = {"error": str(e)}

            tool_parts.append({
                "functionResponse": {
                    "name": name,
                    "response": result_dict
                }
            })
            
        if tool_parts:
            messages.append({
                "role": "function", # role must be 'function' for tool responses in Gemini
                "parts": tool_parts
            })

if __name__ == "__main__":
    main()
