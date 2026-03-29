import os
import json
from src.logger import get_logger
from src.tools import TOOLS

logger = get_logger("Orchestrator")

def main():
    logger.info("Starting Orchestrator for Z0305 (savethem)")
    
    # Phase 1: Discovery
    # We query toolsearch to find all tools for map, rules, and vehicles.
    logger.info("=== PHASE 1: DISCOVERY ===")
    discovered_tools = TOOLS["run_discovery"]()
    
    logger.info(f"Discovery phase complete. Tools found: {json.dumps(discovered_tools, indent=2)}")
    
    # Phase 1.5: Data Collection
    logger.info("=== PHASE 1.5: DATA COLLECTION ===")
    TOOLS["collect_data"](discovered_tools)
    
    logger.info("Data Collection phase complete. Raw data saved to output/raw_data.json")
    
    # Phase 2: Prompt Creation
    logger.info("=== PHASE 2: PROMPT CREATION ===")
    raw_data_path = os.path.join(os.path.dirname(__file__), 'output', 'raw_data.json')
    planner_prompt = TOOLS["generate_planner_prompt"](raw_data_path)
    
    logger.info("Prompt Creation phase complete. System Prompt saved to output/planner_system_prompt.md")

    # Phase 3 & 4: Planner & Submit Feedback Loop
    logger.info("=== PHASE 3 & 4: PLANNER & SUBMIT ===")
    prompt_path = os.path.join(os.path.dirname(__file__), 'output', 'planner_system_prompt.md')
    
    max_attempts = 5
    previous_attempts = []
    
    for attempt in range(max_attempts):
        logger.info(f"--- ATTEMPT {attempt + 1}/{max_attempts} ---")
        
        try:
            calculated_path = TOOLS["compute_path"](prompt_path, previous_attempts)
            logger.info(f"Planner computed path: {calculated_path}")
            
            verification_result = TOOLS["verify_path"](calculated_path)
            
            # API centrala verification typically returns code 0 and "flag" on success
            code = verification_result.get("code", 0)
            message = verification_result.get("message", "")
            
            if code == 0 and ("FLG" in str(verification_result).upper() or "flag" in str(verification_result).lower()):
                 logger.info(f"SUCCESS! Flag captured: {verification_result}")
                 break
            elif code < 0 or "FLG" not in str(verification_result).upper():
                 logger.warning(f"Failed attempt {attempt + 1}. Adding to feedback loop.")
                 previous_attempts.append({
                     "path": calculated_path,
                     "result": verification_result
                 })
                     
        except Exception as e:
             logger.error(f"Error during attempt {attempt + 1}: {e}")
             previous_attempts.append({
                 "path": "Failed to generate valid JSON path",
                 "result": {"error": str(e)}
             })

    logger.info("Orchestrator finished.")

if __name__ == "__main__":
    main()
