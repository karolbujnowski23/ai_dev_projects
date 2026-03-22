import re
import os

LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'failure.log')

def search_logs(query, limit=50):
    """Searches the log file for lines matching the query string."""
    results = []
    
    if not os.path.exists(LOG_FILE_PATH):
        return f"Error: Log file not found at {LOG_FILE_PATH}"
        
    try:
        with open(LOG_FILE_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                if query.lower() in line.lower():
                    results.append(line.strip())
                    if len(results) >= limit:
                        break
        
        if not results:
            return f"No matches found for '{query}'"
            
        return "\n".join(results)
    except Exception as e:
        return f"Error reading logs: {str(e)}"

def count_tokens(text):
    """Rough estimation of token count based on typical word-to-token ratio (1 word ~ 1.3 tokens)."""
    # A simple approximation since we don't want to bring in a full tokenizer library just for this
    words = text.split()
    estimated_tokens = int(len(words) * 1.5) + text.count('\n') * 2
    return estimated_tokens

def format_log_line(log_entry):
    """
    Ensures log entry matches the required format:
    - [YYYY-MM-DD HH:MM] [LEVEL] description
    """
    # Try to extract the timestamp and make sure seconds are removed if present
    match = re.search(r'\[(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})(?::\d{2})?\]\s+\[(.*?)\]\s+(.*)', log_entry)
    if match:
        date, time, level, msg = match.groups()
        return f"[{date} {time}] [{level}] {msg}"
    return log_entry
