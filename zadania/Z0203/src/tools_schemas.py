"""
tools_schemas.py — JSON Schema definitions for LLM tools.
Import TOOL_SCHEMAS into your agent and pass it to the `tools` parameter
when calling the LLM API.
"""

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "check_token_count",
            "description": "Checks the number of tokens in a given text string and compares it against a maximum limit (default 1500). Useful for making sure logs fit within context limits.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text or prompt to calculate the token count for."
                    },
                    "max_tokens": {
                        "type": "integer",
                        "description": "The maximum allowed number of tokens. Defaults to 1500.",
                        "default": 1500
                    }
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "optimize_logs",
            "description": "Optimizes and compresses the given logs by removing unnecessary words or events, based on optimization_prompt.md. Returns the optimized logs as a string.",
            "parameters": {
                "type": "object",
                "properties": {
                    "logs_content": {
                        "type": "string",
                        "description": "The raw or previous iteration of logs to be optimized."
                    }
                },
                "required": ["logs_content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_local_logs",
            "description": "Searches the massive local log file (`failure.log`) for any lines containing specific keywords. Use this to quickly filter logs before full LLM analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "A list of strings to search for, e.g. ['CRIT', 'ECCS8', 'WTRPMP']."
                    }
                },
                "required": ["keywords"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extract_missing_keywords",
            "description": "Given feedback from the technicians, extracts the missing component names or IDs as keywords to use for further log searching.",
            "parameters": {
                "type": "object",
                "properties": {
                    "feedback": {
                        "type": "string",
                        "description": "The exact feedback string from the Central Hub."
                    }
                },
                "required": ["feedback"]
            }
        }
    }
]
