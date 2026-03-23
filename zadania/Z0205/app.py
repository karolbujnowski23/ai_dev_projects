import os
import sys
import json
import base64
import requests
import re
from pathlib import Path

# sys.path modification is no longer needed since app.py is in the root
# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config import APIKEY
from src.logger import logger
from src.api import call_gemini, extract_gemini_text
from src.tools import drone_verify

def main():
    logger.info("Starting Drone Mission Application (Z0205)")
    
    # --- PHASE 1: Vision (gemini-3-flash-preview) ---
    logger.info("Phase 1: Downloading map and analyzing with Vision Model")
    map_url = f"https://hub.ag3nts.org/data/{APIKEY}/drone.png"
    
    try:
        r_img = requests.get(map_url, timeout=30)
        r_img.raise_for_status()
        img_b64 = base64.b64encode(r_img.content).decode('utf-8')
        logger.info("Map image downloaded and encoded.")
    except Exception as e:
        logger.error(f"Failed to download map image: {e}")
        return

    vision_prompt = "Analyze this image and tell me how many rows and columns it has. The image rows and columns are separated by red web of vertical and horizontal lines. Then, identify the sector (column, row) that contains the dam with the blue water. Use 1-based indexing for columns and rows, starting from the top-left corner. Format: (x,y) -no spaces. try to assess the altitude of the point the picture was made. format: (100m) - no spaces!"
    
    messages_vision = [{
        "role": "user",
        "parts": [
            {
                "inline_data": {
                    "mime_type": "image/png",
                    "data": img_b64
                }
            },
            {"text": vision_prompt}
        ]
    }]
    
    vision_response = call_gemini(messages_vision, model="gemini-3-flash-preview")
    vision_text = extract_gemini_text(vision_response)
    logger.info(f"Vision Response:\n{vision_text}")
    
    # Fallback coordinates just in case the extraction fails
    default_coords = "(3,4)"
    
    # --- PHASE 2: Initial instruction generation (gemini-2.5-flash) ---
    logger.info("Phase 2: Generating initial drone instructions")
    
    # Read manuals
    manual_path = os.path.join(os.path.dirname(__file__), 'drone_manual.md')
    with open(manual_path, 'r', encoding='utf-8') as f:
        manual_text = f.read()
        
    system_prompt = f"""You are a Drone Operator.
    You must construct a JSON sequence of instructions for the drone API to destroy the target.
    
    Drone API Manual:
    {manual_text}
    
    Mission parameters:
    - Target ID: PWR6132PL
    - Required altitude: Extract from Vision Report or default to 100m.
    - Mission goal: photograph, then destroy the dam, then return.
    - Post-destroy power: 10%
    - Coordinates of the target are derived from the Vision analysis report.
    - Perform a full calibration of systems before flight (GPS, Compass, selfCheck).
    
    You must output ONLY valid JSON format containing a list of strings, corresponding to the "instructions" array.
    No backticks, no markdown, just JSON. Example:
    [
      "calibrateGPS",
      "setDestinationObject(ABC)",
      "set(1,1)",
      "set(100m)",
      ...
    ]
    """
    
    agent_prompt = f"Vision Model Report on Target Location:\n{vision_text}\nBased on this, generate the initial instruction sequence to destroy the target. Remember to output ONLY the JSON array."
    
    messages_agent = [{"role": "user", "parts": [{"text": agent_prompt}]}]
    
    # --- PHASE 3: Reactive Loop ---
    max_attempts = 8
    
    for attempt in range(max_attempts):
        logger.info(f"Agent Attempt {attempt+1}")
        agent_response = call_gemini(messages_agent, model="gemini-2.5-flash", system_prompt=system_prompt)
        instructions_text = extract_gemini_text(agent_response)
        logger.info(f"Agent Attempt {attempt+1} raw output:\n{instructions_text}")
        
        # Clean JSON
        clean_text = instructions_text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        elif clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        clean_text = clean_text.strip()
            
        try:
            instructions_list = json.loads(clean_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            messages_agent.append({"role": "model", "parts": [{"text": instructions_text}]})
            messages_agent.append({"role": "user", "parts": [{"text": "Your output was not valid JSON. Please return ONLY a valid JSON array of strings, without any markdown or extra text."}]})
            continue
            
        logger.info(f"Verifying instructions via Hub API: {instructions_list}")
        verify_result = drone_verify(instructions_list)
        
        # Check success or errors
        result_str = str(verify_result)
        if "FLG" in result_str or "{{FLG:" in result_str:
            logger.info(f"SUCCESS! Flag obtained: {verify_result}")
            print(f"\nMISSION ACCOMPLISHED!\nResponse:\n{json.dumps(verify_result, indent=2)}")
            break
        elif "message" in verify_result:
            error_msg = verify_result['message']
            logger.warning(f"Hub API rejected instructions: {error_msg}")
            
            # Feed back the error to the agent
            messages_agent.append({"role": "model", "parts": [{"text": json.dumps(instructions_list)}]})
            messages_agent.append({"role": "user", "parts": [{"text": f"The API rejected these instructions with this error message: '{error_msg}'. Please carefully read the Drone Manual again to see what parameter or command is incorrect, missing, or out of order. Provide the fully corrected JSON array of instructions."}]})
        elif "error" in verify_result:
            logger.error(f"Network/API Error: {verify_result['error']}")
            break
        else:
            logger.info(f"Unknown API response format: {verify_result}")
            break

if __name__ == "__main__":
    main()
