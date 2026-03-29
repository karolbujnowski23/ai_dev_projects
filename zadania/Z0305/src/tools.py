import json
import os
import requests
from src.config import APIKEY
from src.logger import get_logger
from src.api import call_llm

logger = get_logger("Tools")

def query_hub_tool(url: str, query: str) -> dict:
    """
    Sends a query to a specific hub endpoint.
    Used for toolsearch and for calling the specific tools discovered.
    """
    payload = {
        "apikey": APIKEY,
        "query": query
    }
    
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()

def toolsearch(query: str) -> dict:
    """
    Wrapper around the main toolsearch endpoint.
    """
    url = "https://hub.ag3nts.org/api/toolsearch"
    return query_hub_tool(url, query)

def run_discovery() -> dict:
    logger.info("Starting Discovery Phase...")
    keywords = ["map", "terrain rules", "vehicles", "Skolwin","maual","guide","instructions","notes", "note", "book"]
    discovered_tools = {}

    for kw in keywords:
        logger.info(f"Searching tools for keyword: '{kw}'")
        try:
            results = toolsearch(kw)
            logger.info(f"Discovered tools for '{kw}': {json.dumps(results, indent=2)}")
            discovered_tools[kw] = results
        except Exception as e:
            logger.error(f"Failed to search for '{kw}': {e}")
            
    output_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'discovered_tools.json')
    with open(output_path, 'w') as f:
        json.dump(discovered_tools, f, indent=4)
    logger.info(f"Saved discovered tools to {output_path}")
    return discovered_tools

def collect_data(discovered_tools: dict) -> dict:
    logger.info("Starting data collection from discovered tools...")
    raw_knowledge = {}
    
    try:
        logger.info("Calling verify_path with ['check'] to get possible parameters.")
        check_result = verify_path(["check"])
        raw_knowledge["verify_rules"] = [check_result]
    except Exception as e:
        logger.error(f"Failed to query verify_path with ['check']: {e}")
    
    prompt_path = os.path.join(os.path.dirname(__file__), 'query_reasoner.prompt.md')
    if not os.path.exists(prompt_path):
        logger.error(f"Query reasoner prompt not found at {prompt_path}")
        return {}
    with open(prompt_path, 'r', encoding='utf-8') as f:
        reasoner_prompt_template = f.read()
    
    for category, response in discovered_tools.items():
        url_base = "https://hub.ag3nts.org"
        
        logger.info(f"Processing category: {category}")
        if response.get('message') == 'Matching tools found.':
            tools_list = response.get('tools', []) if isinstance(response, dict) else response
            logger.info(f"tool_list{tools_list}")

           
            for tool_info in tools_list:
                if not isinstance(tool_info, dict):
                    continue
                url = tool_info.get('url') or tool_info.get('endpoint') or tool_info.get('api_url')
                name = tool_info.get('name', 'Unknown Tool')
                description = tool_info.get('description', '')
                logger.info(f"Found tool: {name} - {description}")
                parameters = tool_info.get('parameter', {})
                if not url:
                    continue
                logger.info(f"Reasoning query for tool: {name} at {url}")
                tool_def_json = json.dumps(tool_info, indent=2)
                
                # Extract content after frontmatter
                parts = reasoner_prompt_template.split('---', 2)
                prompt_content = parts[-1].strip() if len(parts) > 2 else reasoner_prompt_template
                reasoner_prompt = prompt_content.replace('{{tool_definition}}', tool_def_json)
                
                query_string = category
                # If this is the map category, we loop until we get valid map data
                max_map_retries = 5
                retries = 0
                success = False
                
                while not success and retries < max_map_retries:
                    try:
                        reasoning_response = call_llm(reasoner_prompt, model="gemini-2.5-flash")
                        response_text = reasoning_response['candidates'][0]['content']['parts'][0]['text']
                        
                        # Clean up markdown JSON formatting
                        if response_text.startswith("```json"): response_text = response_text[7:]
                        if response_text.startswith("```"): response_text = response_text[3:]
                        if response_text.endswith("```"): response_text = response_text[:-3]
                        response_text = response_text.strip()
                        
                        reasoning_data = json.loads(response_text)
                        query_string = reasoning_data.get('query', category)
                        logger.info(f"Generated query (Attempt {retries+1}): '{query_string}' (Reasoning: {reasoning_data.get('reasoning', 'None')})")
                    except Exception as e:
                        logger.error(f"Failed to generate query for {name}, falling back to category '{category}': {e}")
                    
                    logger.info(f"Querying tool: {name} at {url} with query '{query_string}'")
                    try:
                        result = query_hub_tool(url_base + url, query=query_string)
                        
                        # Check if it actually returned the map or just a generic error message
                        if category == "map" and ("message" in result and "No matching" in str(result)):
                            logger.warning(f"Map tool returned empty/no match for query '{query_string}'. Retrying...")
                            retries += 1
                            continue
                            
                        if category not in raw_knowledge:
                            raw_knowledge[category] = []
                        raw_knowledge[category].append({
                            "tool_info": tool_info,
                            "result": result
                        })
                        logger.info(f"Successfully collected data from {name}")
                        success = True
                    except Exception as e:
                        logger.error(f"Failed to query tool {name} at {url}: {e}")
                        retries += 1
                        
                if category == "map" and not success:
                    logger.error(f"CRITICAL: Failed to retrieve map data from {name} after {max_map_retries} retries. Planning will fail.")

    if not raw_knowledge:
        logger.error("No data was collected from the discovered tools. raw_data.json would be empty.")
        raise ValueError("raw_data.json is empty. Cannot proceed with planning without data.")

    output_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'raw_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(raw_knowledge, f, indent=4, ensure_ascii=False)
    logger.info(f"Finished data collection. Saved to {output_path}")
    return raw_knowledge

def generate_planner_prompt(raw_data_path: str) -> str:
    logger.info("Starting Prompt Creator Phase...")
    with open(raw_data_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    raw_data_str = json.dumps(raw_data, indent=2, ensure_ascii=False)
    instruction = f"""
You are an expert Prompt Engineer and System Architect.
I am providing you with raw data collected from various API endpoints regarding a 10x10 map, terrain rules, and vehicle stats.

Your task is to analyze this raw data and generate a highly detailed SYSTEM PROMPT. 
This SYSTEM PROMPT will be used by another AI Agent (the "Planning Agent") to calculate the shortest path to a city called 'Skolwin'.
The route from stert to destination must be shortest possible adhering to the constraints of 10 FOOD and 10 FUEL.

The raw data:
{raw_data_str}

Important context for the Planning Agent:
- The map is 10x10.
- The goal is to reach 'Skolwin'.
- We start with 10 units of FOOD and 10 units of FUEL.
- The path must be an array of strings, e.g., ["vehicle_name", "right", "up", "down", ...].
- You can change vehicles or abandon them to walk at any time, but only ONCE. If selected "dismount"- do NOT select any other vehicle name or "walk".
- Resource constraints are strict.

OUTPUT FORMAT:
Output ONLY the final Markdown formatted System Prompt. Do not include introductory or concluding conversational text. 
Ensure the prompt clearly lists:
1. The Map grid and start/end coordinates (deduce from raw data if possible).
2. The exact Fuel and Food costs for each terrain type for each vehicle (and walking).
3. The exact Rules for resource consumption.
4. Clear instructions on how the Planning Agent should format its final output.
"""
    logger.info("Sending request to Gemini to generate the Planner System Prompt...")
    response = call_llm(instruction, model="gemini-2.5-pro")
    
    prompt_text = response['candidates'][0]['content']['parts'][0]['text']
    if prompt_text.startswith("```markdown"): prompt_text = prompt_text[11:]
    if prompt_text.startswith("```"): prompt_text = prompt_text[3:]
    if prompt_text.endswith("```"): prompt_text = prompt_text[:-3]
    prompt_text = prompt_text.strip()
    
    output_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'planner_system_prompt.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(prompt_text)
    logger.info(f"Successfully generated and saved Planner System Prompt to {output_path}")
    return prompt_text

def compute_path(prompt_path: str, previous_attempts: list = None) -> list:
    logger.info("Starting Planner Phase...")
    with open(prompt_path, 'r', encoding='utf-8') as f:
        system_prompt = f.read()

    feedback_context = ""
    if previous_attempts:
        feedback_context = "\n\n--- PREVIOUS FAILED ATTEMPTS AND FEEDBACK ---\n"
        for i, attempt in enumerate(previous_attempts):
            feedback_context += f"Attempt {i+1} Exact Path Sequence You Submitted: {json.dumps(attempt['path'])}\n"
            feedback_context += f"API Rejection Reason / Error: {json.dumps(attempt['result'])}\n\n"
        feedback_context += "CRITICAL FEEDBACK INSTRUCTION:\n"
        feedback_context += "1. Analyze the exact path sequences you submitted above.\n"
        feedback_context += "2. Figure out EXACTLY why that specific path failed (e.g., ran out of fuel, wrong vehicle, hit an impassable rock on turn 1).\n"
        feedback_context += "3. DO NOT repeat the same path sequence. You MUST generate a completely new route that avoids the specific failure point of your previous attempts.\n"

    instruction = f"""
You are the Planning Agent.
Read the following SYSTEM PROMPT which contains all rules, map data, and vehicle stats.

{system_prompt}
{feedback_context}

CRITICAL RULES TO AVOID COMMON MISTAKES:
1. Pay very close attention to your FIRST MOVES. Look at the map grid carefully.
2. If there is an obstacle (e.g., a rock, a tree, or river) on the tile immediately in front of you (e.g., to your right), YOU CANNOT JUST MOVE INTO IT. You must either use a vehicle that can traverse that terrain type, or path *around* it (e.g. go 'up' or 'down' first).
3. Track your 10 FOOD and 10 FUEL exactly on a piece of paper as you plan each step.
4. The first element of the array MUST be the vehicle name, followed by directions ("up", "down", "left", "right").
5. YOU CANNOT START FROM THE RIGHT WHERE THERE IS A ROCK ON THE RIGHT! DO NOT GO RIGHT ON YOUR VERY FIRST MOVE!

TASK:
Calculate the shortest possible path from the start point to Skolwin, adhering strictly to the 10 FOOD and 10 FUEL constraints.

OUTPUT:
Output ONLY a valid JSON array of strings representing your steps, and absolutely nothing else. No markdown, no explanation.
Example format:
["vehicle_name", "right", "up", "right", "down"]
"""
    logger.info("Sending pathfinding request to Gemini...")
    response = call_llm(instruction, model="gemini-3.1-pro-preview")
    
    response_text = response['candidates'][0]['content']['parts'][0]['text']
    if response_text.startswith("```json"): response_text = response_text[7:]
    if response_text.startswith("```"): response_text = response_text[3:]
    if response_text.endswith("```"): response_text = response_text[:-3]
    response_text = response_text.strip()
    
    path_array = json.loads(response_text)
    logger.info(f"Successfully computed path with {len(path_array)} steps.")
    return path_array

def verify_path(path: list) -> dict:
    logger.info(f"Starting submission to /verify with path length: {len(path)}")
    url = "https://hub.ag3nts.org/verify"
    payload = {
        "apikey": APIKEY,
        "task": "savethem",
        "answer": path
    }
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, json=payload, headers=headers)
    
    try:
        result = response.json()
    except Exception:
        result = {"error": response.text, "status_code": response.status_code}
        
    if not response.ok:
        logger.warning(f"Verification returned error {response.status_code}: {result}")
    else:
        logger.info(f"Verification successful: {result}")
        
    return result

# Tool Schema for Orchestrator
TOOLS = {
    "run_discovery": run_discovery,
    "collect_data": collect_data,
    "generate_planner_prompt": generate_planner_prompt,
    "compute_path": compute_path,
    "verify_path": verify_path
}
