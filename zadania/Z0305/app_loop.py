import os
import json
from src.logger import get_logger
from src.tools import TOOLS

logger = get_logger("Orchestrator-Loop")

def main():
    logger.info("Starting Orchestrator iteration loop for Z0305 (savethem)")
    
    # Phase 3 & 4: Planner & Submit Feedback Loop ONLY
    # Skipping Discovery, Data Collection, and Prompt Creation.
    logger.info("=== PHASE 3 & 4: PLANNER & SUBMIT (ITERATION ONLY) ===")
    prompt_path = os.path.join(os.path.dirname(__file__), 'output', 'planner_system_prompt.md')
    
    if not os.path.exists(prompt_path):
        logger.error(f"System prompt not found at {prompt_path}. Please run the full app.py first.")
        return
    
    max_attempts = 5 # Increased since we're only focusing on iterations
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

    logger.info("Orchestrator loop finished.")

if __name__ == "__main__":
    main()
