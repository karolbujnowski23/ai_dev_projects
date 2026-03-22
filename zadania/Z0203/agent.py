import os
import requests
import time
from dotenv import load_dotenv

from src.api import verify_logs, generate_content
from src.config import APIKEY

from src.tools import check_token_count, optimize_logs, search_local_logs, extract_missing_keywords
from src.tools_schemas import TOOL_SCHEMAS

# -----------------
# TOOL MAP DO OBSŁUGI LLM
# -----------------
TOOL_MAP = {
    "check_token_count": check_token_count,
    "optimize_logs": optimize_logs,
    "search_local_logs": search_local_logs,
    "extract_missing_keywords": extract_missing_keywords
}
LOG_FILE = "failure.log"

def ensure_log_downloaded():
    """Downloads the massive log file if it's not already present locally."""
    if not os.path.exists(LOG_FILE):
        print("[Agent] Downloading massive log file from hub...")
        url = f"https://hub.ag3nts.org/data/{APIKEY}/failure.log"
        response = requests.get(url)
        if response.ok:
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                f.write(response.text)
            print("[Agent] Log file downloaded and saved locally.")
        else:
            raise Exception(f"Failed to download logs: {response.text}")

def smart_filter(lines):
    """Keeps the first and last occurrence of every identical message block (boundary filtering)."""
    if not lines: return []
    filtered = []
    
    # Pre-parse messages for comparison
    parsed = []
    for line in lines:
        msg = line[21:].strip() if len(line) > 21 else line
        parsed.append(msg)

    for i in range(len(lines)):
        curr_msg = parsed[i]
        prev_msg = parsed[i-1] if i > 0 else None
        nxt_msg = parsed[i+1] if i < len(lines)-1 else None
        
        # Keep if it's the start or end of a block of identical messages
        # OR if it's a CRIT log (though CRIT logs are usually important anyway)
        if curr_msg != prev_msg or curr_msg != nxt_msg or "[CRIT]" in lines[i]:
            filtered.append(lines[i])
            
    return filtered

def main():
    ensure_log_downloaded()
    
    # Initial setup: Focus on critical errors
    active_keywords = ["CRIT", "ERRO", "WARN"]
    # Będziemy trzymać osobną listę słów wyciągniętych od Hubu
    hub_keywords = []
    
    # Upewniamy się, że folder temp_logs istnieje
    os.makedirs("temp_logs", exist_ok=True)
    
    # WYKONAJ WSTĘPNE FILTROWANIE TYLKO RAZ (zapis do temp_logs/base_filtered.log)
    print("[Agent] Wykonuję jednorazowe wstępne filtrowanie potężnego pliku...")
    initial_raw_logs = search_local_logs(active_keywords)

    # Nie deduplikujemy logów, aby nie stracić osi czasu powtarzających się zdarzeń
    processed_initial_raw_logs = []
    for line in initial_raw_logs.split('\n'):
        if line.strip():
            processed_initial_raw_logs.append(line)
    
    initial_raw_logs = "\n".join(processed_initial_raw_logs)
    
    base_filtered_path = "temp_logs/base_filtered.log"
    with open(base_filtered_path, "w", encoding="utf-8") as bf:
        bf.write(initial_raw_logs)

    MAX_ITERATIONS = 5
    raw_history_set = set()

    for i in range(MAX_ITERATIONS):
        print(f"\n================ ITERATION {i+1} ================")
        
        if i == 0:
            # Iteracja 1 - bazujemy na już wcześniej utworzonym, odfiltrowanym base_filtered.log
            with open(base_filtered_path, "r", encoding="utf-8") as bf:
                for line in bf:
                    if line.strip():
                        raw_history_set.add(line.strip())
        else:
            # Wyszukujemy nowe słowa w logach z zadaną datą
            new_raw_logs = search_local_logs(hub_keywords, i) if hub_keywords else ""
            for line in new_raw_logs.split('\n'):
                if line.strip():
                    raw_history_set.add(line.strip())

        # Sortujemy i filtrujemy historię
        sorted_history = sorted(list(raw_history_set))
        
        # Odrzuć niechciane wpisy - wstępna pre-kompresja
        # Dynamiczny filtr - uwzględnia nasze słowa startowe ORAZ te z feedbacku
        filter_words = ["CRIT", "WARN", "ERRO", "FIRMWARE"] + hub_keywords
        
        important_lines = []
        for line in sorted_history:
            line_upper = line.upper()
            if any(kw.upper() in line_upper for kw in filter_words) and "2026-03-21" in line:
                important_lines.append(line)
        
        # Stosujemy inteligentny filtr deduplikujący czasowo
        final_raw_logs_list = smart_filter(important_lines)
        logs = "\n".join(final_raw_logs_list)
        
        # 2. Optimize and Compress logs (LLM prompt caching utilized here)
        print(f"[Agent] Optimizing and compressing {len(final_raw_logs_list)} logs via LLM...")
        optimized_logs = optimize_logs(logs, focus_keywords=hub_keywords)
        
        # Bezpieczne usunięcie bloków kodu Markdown
        optimized_logs = optimized_logs.strip()
        if optimized_logs.startswith("```"):
            lines = optimized_logs.split('\n')
            if len(lines) > 1 and lines[0].startswith("```"):
                lines = lines[1:]
            if len(lines) > 0 and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            optimized_logs = '\n'.join(lines).strip()
        
        # 3. Token check
        token_info = check_token_count(optimized_logs, max_tokens=1500)
        print(f"[Agent] Token count: {token_info['token_count']} / 1500")
        
        # Zapisz zoptymalizowane logi z tej iteracji do pliku w temp_logs
        with open(f"temp_logs/iteration_{i+1}.log", "w", encoding="utf-8") as f_temp:
            f_temp.write(optimized_logs)
            
        if not token_info["is_within_limit"]:
            print("[Agent] WARNING: Token limit exceeded! Enforcing double compression...")
            # Enforce harder compression with same prefix for Cache Hit
            optimized_logs = optimize_logs(optimized_logs + "\n\nCRITICAL SYSTEM MESSAGE: Your output is STILL OVER 1500 TOKENS! You MUST DROP less critical WARN events and compress EVERYTHING drastically. Do NOT return more than 50 lines total.")
            optimized_logs = optimized_logs.strip()
            if optimized_logs.startswith("```"):
                lines = optimized_logs.split('\n')
                if len(lines) > 1 and lines[0].startswith("```"):
                    lines = lines[1:]
                if len(lines) > 0 and lines[-1].strip().startswith("```"):
                    lines = lines[:-1]
                optimized_logs = '\n'.join(lines).strip()
        
        # 4. Verification with Central Hub
        print("[Agent] Sending to Central Hub for verification...")
        try:
            result = verify_logs(optimized_logs)
            message = result.get("message", "")
            code = result.get("code", 0)
            print(f"[Central Hub Response]: Code: {code} - {message}")
            
            # 5. Check for flag
            if "FLG:" in message or code == 0:
                print("\n[SUCCESS] Successfully recovered logs and obtained the flag!")
                print(f"Flag: {message}")
                break
                
            # 6. Analyze feedback and create feedback loop
            if "context window" in message.lower() or "compression" in message.lower() or code == -940:
                print("[Agent] Feedback: logs are too long. The compression will be more aggressive in the next turn.")
                
            elif "unable to determine" in message.lower() or "do not know what happened to" in message.lower() or "device" in message.lower() or "too short" in message.lower() or "add more lines" in message.lower() or code in [-948, -949, -960]:
                print("[Agent] Received missing info list in error. Analyzing feedback via LLM...")
                new_keys = extract_missing_keywords(message)
                print(f"[Agent] New keywords to add to local search: {new_keys}")
                
                added = False
                for kw in new_keys:
                    kw_up = kw.upper()
                    if kw_up and kw_up not in hub_keywords:
                        hub_keywords.append(kw_up)
                        added = True
                        
                if not added:
                    print("[Agent] No new specific components found from Hub...")
            else:
                print(f"[Agent] Unexpected verification response: {message}. Trying again...")

        except Exception as e:
            print(f"[CRITICAL ERROR] Unknown failure: {e}")
            break
            
        # Avoid rate limiting
        time.sleep(2)

if __name__ == "__main__":
    main()
