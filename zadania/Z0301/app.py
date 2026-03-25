import json
import os
import logging
from src.config import API_KEY, TASK_NAME, MODEL_CONFIG
from src.api import GeminiClient, CentralaClient, logger
from src.validators import load_all_sensors

def main():
    logger.info("Starting evaluation task.")
    
    # Paths
    sensors_dir = os.path.join(os.path.dirname(__file__), 'sensors')
    prompt_file = os.path.join(os.path.dirname(__file__), 'prompt.md')
    
    # 1. Load system prompt from prompt.md
    with open(prompt_file, 'r', encoding='utf-8') as f:
        system_prompt = f.read()
        
    # 2. Load all sensor technical data
    sensors_data = load_all_sensors(sensors_dir)
    
    # 3. Separate FAILED and OK, deduplicate OK patterns for LLM
    recheck_ids = set()
    unique_ok_patterns = {} # (sensor_type, readings_tuple, note) -> [sensor_ids]
    
    for file_id, info in sensors_data.items():
        if info['technical_status'] == 'FAILED':
            recheck_ids.add(file_id)
            continue
            
        # Technically OK sensors - check for logical inconsistencies with LLM
        note = info['data'].get('operator_notes', '')
        sensor_type = info['data'].get('sensor_type', 'unknown')
        
        # Extract readings (exclude non-measurement fields)
        readings = {k: v for k, v in info['data'].items() if k not in ('timestamp', 'operator_notes', 'sensor_type') and v != 0}
        readings_tuple = tuple(sorted(readings.items()))
        
        pattern = (sensor_type, readings_tuple, note)
        if pattern not in unique_ok_patterns:
            unique_ok_patterns[pattern] = []
        unique_ok_patterns[pattern].append(file_id)
        
    logger.info(f"Technically failed: {len(recheck_ids)} files.")
    logger.info(f"Technically OK: {len(sensors_data) - len(recheck_ids)} files. Found {len(unique_ok_patterns)} unique patterns to check with LLM.")
    
    # 4. Use LLM to classify unique OK patterns
    llm_input = {}
    pattern_keys = []
    for i, (pattern, _) in enumerate(unique_ok_patterns.items()):
        key = f"u{i}"
        llm_input[key] = {
            "sensor_type": pattern[0],
            "readings": dict(pattern[1]),
            "operator": pattern[2],
            "status": "OK"
        }
        pattern_keys.append(pattern)
        
    gemini = GeminiClient(model=MODEL_CONFIG['classifier'])
    
    user_prompt = json.dumps(llm_input, indent=2)
    inconsistent_unique_keys = gemini.call(system_prompt, user_prompt)
    
    if inconsistent_unique_keys is None:
        logger.error("Failed to receive classification from Gemini.")
        return
        
    # 5. Add IDs from LLM-flagged patterns to recheck list
    for key in inconsistent_unique_keys:
        if key.startswith('u'):
            idx = int(key[1:])
            pattern = pattern_keys[idx]
            ids = unique_ok_patterns[pattern]
            recheck_ids.update(ids)
            
    logger.info(f"Total IDs to recheck: {len(recheck_ids)}")
    logger.info(f"Recheck IDs: {sorted(list(recheck_ids))}")
    # 6. Submit to Centrala
    final_recheck = sorted(list(recheck_ids))
    centrala = CentralaClient(API_KEY)
    response = centrala.submit(TASK_NAME, {"recheck": final_recheck})
    
    if response:
        print(f"Submission results: {json.dumps(response, indent=2)}")

if __name__ == "__main__":
    main()
