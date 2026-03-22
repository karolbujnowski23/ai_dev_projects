"""
tools.py — Reusable tool functions and JSON Schema definitions for LLM.
Includes a tool to check the number of tokens of a given prompt.
"""

import tiktoken
import os
from src.api import generate_content

def check_token_count(text: str, max_tokens: int = 1500) -> dict:
    """
    Counts the number of tokens in the given text using tiktoken (cl100k_base encoding).
    Returns a dictionary containing the token count and a boolean indicating
    if it's within the max_tokens limit.
    """
    try:
        # Since we use Gemini 2.5 Flash, cl100k_base (from OpenAI) is just an approximation. 
        # Gemini uses its own tokenizer (SentencePiece), but tiktoken with cl100k_base 
        # is a very close and conservative proxy for checking the ~1500 token limit.
        encoding = tiktoken.get_encoding("cl100k_base")
    except Exception as e:
        print(f"[Warning] Tokenizer error: {e}. Falling back to char count heuristic.")
        estimated_token_count = len(text) // 4
        return {
            "token_count": estimated_token_count,
            "max_tokens": max_tokens,
            "is_within_limit": estimated_token_count <= max_tokens
        }
        
    token_count = len(encoding.encode(text))
    
    return {
        "token_count": token_count,
        "max_tokens": max_tokens,
        "is_within_limit": token_count <= max_tokens
    }

def optimize_logs(logs_content: str, focus_keywords: list = None) -> str:
    """
    Optimizes and compresses the given logs by using the Gemini model.
    It reads the optimization instructions from optimization_prompt.md.
    """
    prompt_path = os.path.join(os.path.dirname(__file__), '..', 'optimization_prompt.md')
    
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            system_prompt = f.read()
    except FileNotFoundError:
        system_prompt = "You are an AI that optimizes and compresses system logs. Please shorten the following logs while keeping crucial timestamps, components, and severity levels intact."
        
    focus_msg = ""
    if focus_keywords:
        focus_msg = f"\n\nCRITICAL FOCUS: The following components are under investigation: {', '.join(focus_keywords)}. Ensure you include ALL relevant events for these components and keep them detailed."

    # We pass the large static prompt FIRST as part of the text so that Gemini can cache it over multiple requests
    full_prompt = f"{system_prompt}{focus_msg}\n\nLogs to optimize:\n{logs_content}"
    
    try:
        # Generate content with caching in mind (the first ~1000 tokens of system_prompt will trigger caching automatically in Gemini >=1.5 if sent repeatedly)
        optimized_logs = generate_content(full_prompt)
        return optimized_logs
    except Exception as e:
        return f"Error during optimization: {str(e)}"


def search_local_logs(keywords: list, iteration: int = 0 , log_file_name: str = 'failure.log') -> str:
    """Local RAG / grep subagent to filter logs without spending tokens on LLM."""
    print(f"\n[Agent] Searching local logs for keywords: {keywords}")
    found_lines = []
    
    # Próbujemy znaleźć plik z logami
    log_file = os.path.join(os.path.dirname(__file__), '..', log_file_name)
    
    if not os.path.exists(log_file):
        return f"File {log_file} does not exist."
        
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            if "2026-03-21" in line and any(keyword in line for keyword in keywords):
                found_lines.append(line.strip())
    
    return "\n".join(found_lines)

def extract_missing_keywords(feedback: str) -> list:
    """Subagent analyzing feedback to extract missing components for the next iteration."""
    prompt = f"""
    You are an intelligent message parser. Extract the specific missing component ID from the technicians' feedback.
    The component is usually a capitalized device code (e.g., STMTURB12, PWR01, FIRMWARE, ECCS8, WTRPMP, WTANK07).
    It might be wrapped in quotes or specified clearly in the text.
    Return ONLY the exact device name. No conversational text, no punctuation (other than standard ID chars).
    
    Feedback: {feedback}
    """
    response = generate_content(prompt)
    
    # Czyszczenie śmieci (markdown, kropki na końcu, cudzysłowy) z odpowiedzi LLMa
    clean_resp = response.replace('`', '').replace('"', '').replace("'", "").strip('.\n ')
    keywords = [k.strip() for k in clean_resp.split(",") if k.strip()]
    print(f"[Agent] Extracted keywords from feedback: {keywords}")
    return keywords
