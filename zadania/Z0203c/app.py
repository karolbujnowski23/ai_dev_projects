import sys
import os
import json
from config import APIKEY
from api import generate_content, verify_logs
from tools import search_logs, count_tokens, format_log_line, LOG_FILE_PATH

MAX_TOKENS = 1500

system_instruction = """
You are an expert AI agent designed to analyze system logs from a power plant failure and create a highly compressed summary.

Your goal is to extract the critical logs (WARN, ERRO, CRIT) directly related to the failure (power, cooling, pumps, software, and other components) and format them precisely as required.
The total log summary MUST fit within 1500 tokens (approximately 1000-1100 words).

FORMAT REQUIREMENTS:
1. One event per line (do NOT combine events into one line).
2. Date format MUST be YYYY-MM-DD.
3. Time format MUST be HH:MM or H:MM (NO seconds!). Example: `[2026-02-26 06:04]`
4. You can shorten and paraphrase the log message but MUST preserve:
   - The timestamp
   - The severity level ([WARN], [ERRO], [CRIT])
   - The component ID (e.g., ECCS8, PWR01, WTANK07)
   - The core meaning of the event

You have access to a tool to search the logs. Use it to find relevant events.
The failure happened on 2026-03-21.
Look for components mentioned in Central's feedback if you miss anything.

Example valid output log:
[2026-03-21 06:04] [CRIT] ECCS8 runaway outlet temp. Protection interlock initiated reactor trip.
[2026-03-21 06:11] [WARN] PWR01 input ripple crossed warning limits.
[2026-03-21 10:15] [CRIT] WTANK07 coolant below critical threshold. Hard trip initiated.
"""

tools_schema = [
    {
        "functionDeclarations": [
            {
                "name": "search_logs",
                "description": "Searches the log file for lines matching the query string. Good for finding specific components or severity levels.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "query": {
                            "type": "STRING",
                            "description": "The search query, e.g. 'CRIT' or 'PWR01'"
                        },
                        "limit": {
                            "type": "INTEGER",
                            "description": "Max number of results to return (default: 50)"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "submit_logs",
                "description": "Submits the finalized compressed logs to the central system for verification.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "logs": {
                            "type": "STRING",
                            "description": "The formatted log string, with one event per line separated by \\n."
                        }
                    },
                    "required": ["logs"]
                }
            }
        ]
    }
]

def run_agent():
    print("Starting Failure Log Agent...")
    
    # Pre-fetch some initial logs to give the agent context
    initial_crit = search_logs("CRIT", limit=200)
    initial_erro = search_logs("ERRO", limit=200)
    
    prompt = f"""
    The power plant crashed on 2026-03-21. I need you to create a compressed log file under 1500 tokens.
    Start by analyzing the CRIT and ERRO logs, and search for warnings (WARN) on related components.
    
    Here is an initial sample of CRIT logs to start you off:
    {initial_crit[:1000]}...
    
    And some ERRO logs:
    {initial_erro[:1000]}...
    
    Use the search_logs tool to explore further, then use submit_logs to finish.
    """
    
    conversation = [
        {"role": "user", "parts": [{"text": prompt}]}
    ]

    while True:
        # Call Gemini
        print("Calling Gemini API...")
        payload = {
            "contents": conversation,
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "tools": tools_schema
        }
        
        headers = {
            "x-goog-api-key": APIKEY if "gemini" not in APIKEY else GEMINI_LLM_APIKEY, # wait, config uses GEMINI_LLM_APIKEY
            "Content-Type": "application/json"
        }
        import requests
        from config import GEMINI_LLM_APIKEY
        
        response = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
            headers={"x-goog-api-key": GEMINI_LLM_APIKEY, "Content-Type": "application/json"},
            json=payload
        )
        
        data = response.json()
        
        if 'error' in data:
            print(f"API Error: {data['error']}")
            break
            
        candidate = data['candidates'][0]
        content = candidate['content']
        parts = content.get('parts', [])
        
        # Add model response to conversation history
        conversation.append(content)
        
        # Process tool calls
        tool_call_found = False
        for part in parts:
            if 'functionCall' in part:
                tool_call_found = True
                fn_call = part['functionCall']
                fn_name = fn_call['name']
                fn_args = fn_call.get('args', {})
                
                print(f"Agent called tool: {fn_name}({fn_args})")
                
                if fn_name == "search_logs":
                    result = search_logs(fn_args['query'], fn_args.get('limit', 50))
                    
                    # Add tool response to conversation
                    conversation.append({
                        "role": "function",
                        "parts": [
                            {
                                "functionResponse": {
                                    "name": fn_name,
                                    "response": {"result": result}
                                }
                            }
                        ]
                    })
                    
                elif fn_name == "submit_logs":
                    logs = fn_args['logs']
                    
                    # Basic formatting validation before submitting
                    formatted_lines = []
                    for line in logs.split('\n'):
                        line = line.strip()
                        if line:
                            formatted_lines.append(format_log_line(line))
                    formatted_logs = '\n'.join(formatted_lines)
                    
                    tokens = count_tokens(formatted_logs)
                    print(f"Submitting logs (Estimated tokens: {tokens})...")
                    
                    if tokens > 1500:
                        print("Warning: Log might exceed 1500 tokens.")
                    
                    verify_res = verify_logs(APIKEY, formatted_logs)
                    print(f"Verification Result: {json.dumps(verify_res, indent=2)}")
                    
                    # If successful, exit
                    if verify_res.get('code') == 0 or 'FLG' in str(verify_res):
                        print("Success! Flag obtained.")
                        return verify_res
                    
                    # If failed, add the feedback to the conversation
                    conversation.append({
                        "role": "function",
                        "parts": [
                            {
                                "functionResponse": {
                                    "name": fn_name,
                                    "response": {"result": verify_res}
                                }
                            }
                        ]
                    })
                    
                    print("Submission rejected. Informing agent of the feedback...")
                    
        if not tool_call_found:
            text_response = parts[0].get('text', '')
            print(f"Agent says: {text_response}")
            # If agent didn't call a tool but we still need to continue, prompt it
            prompt = "Please use the submit_logs tool to submit your final compressed logs."
            conversation.append({
                "role": "user",
                "parts": [{"text": prompt}]
            })

if __name__ == "__main__":
    run_agent()
