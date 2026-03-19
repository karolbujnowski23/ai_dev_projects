import os
import logging
import time
from dotenv import load_dotenv

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from src.data_ingestion.downloader import fetch_latest_data
from src.hub_communication.client import HubClient, build_prompt_and_classify
from src.prompt_engineering.orchestrator import LLMClient, update_prompt_template
from src.analysis.feedback_analyzer import analyze_feedback

def load_prompt(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def save_prompt(filepath: str, content: str):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    # Wczytanie zmiennych środowiskowych
    config_path = r"C:\Users\buyak\Documents\AI_devs\zadania\.config"
    load_dotenv(dotenv_path=config_path)
    
    OPENROUTER_API_KEY = os.getenv("LLM_APIKEY")
    HUB_API_KEY = os.getenv("APIKEY")
    
    HUB_API_ENDPOINT = "https://hub.ag3nts.org/verify"
    DATA_URL = f"https://hub.ag3nts.org/data/{HUB_API_KEY}/categorize.csv"
    
    if not all([OPENROUTER_API_KEY, HUB_API_KEY]):
        logger.error("Brak wymaganych kluczy API w pliku .config.")
        return

    PROMPT_FILE = "prompts/classification_template.txt"
    static_prompt_base = load_prompt(PROMPT_FILE)
    
    llm_client = LLMClient(OPENROUTER_API_KEY)
    hub_client = HubClient(HUB_API_ENDPOINT, HUB_API_KEY)

    iteration = 1
    while True:
        logger.info(f"--- ROZPOCZĘCIE ITERACJI {iteration} ---")
        try:
            # 1. Zawsze resetujemy licznik i pobieramy nowe dane dla czystego podejścia
            hub_client.send_reset()
            items = fetch_latest_data(DATA_URL)
            
            # 2. Wysyłka promptów do huba
            hub_responses = build_prompt_and_classify(items, static_prompt_base, hub_client)
            
            # Szukamy flagi w odpowiedziach
            success_flag = None
            for resp in hub_responses:
                if isinstance(resp, dict) and "message" in resp and "{{FLG:" in str(resp["message"]):
                    success_flag = resp["message"]
                    break
                    
            if success_flag:
                logger.info(f"SUKCES! Zdobyto flagę: {success_flag}")
                break
            
            # 4. Analiza błędów
            feedback = analyze_feedback(hub_responses)
            logger.info(f"Feedback z huba:\n{feedback}")
            
            if "ERROR" in feedback:
                logger.info("Wykryto błędy w ewaluacji Huba.")
                logger.info("Uruchamianie Agenta Inżynierii Promptów...")
                
                new_prompt = update_prompt_template(feedback, static_prompt_base, OPENROUTER_API_KEY)
                
                if new_prompt and new_prompt != static_prompt_base:
                    save_prompt(PROMPT_FILE, new_prompt)
                    static_prompt_base = new_prompt
                    logger.info(f"Agent zaktualizował szablon promptu na:\n{new_prompt}")
                else:
                    logger.warning("Agent nie zmodyfikował promptu!")
                
                logger.info("Czekam 3 sekundy przed kolejną próbą...")
                time.sleep(3)
            else:
                logger.info("Brak błędów, ale nie znaleziono flagi. Ponawiam...")
                time.sleep(3)
                
        except Exception as e:
            logger.error(f"Wystąpił błąd krytyczny w pętli: {e}")
            time.sleep(5)
            
        iteration += 1

if __name__ == "__main__":
    main()
