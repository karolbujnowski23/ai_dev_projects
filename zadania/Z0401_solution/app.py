import logging
import os
import json
from src.scraper import get_oko_data
from src.api import send_to_centrala

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Orchestrator")

def solve_z0401():
    logger.info("--- Starting Z0401 OKO Editor Solution ---")

    # 1. Scrape IDs
    try:
        ids = get_oko_data()
        skolwin_incident_id = ids["skolwin_incident_id"]
        skolwin_task_id = ids["skolwin_task_id"]
        komarowo_incident_id = "351c0d9c90d66b4c040fff1259dd191d"
    except ValueError as e:
        logger.error(f"Critical error during scraping: {e}")
        return

    # 2. Modify Skolwin Incident Report
    logger.info("Step 2: Modifying Skolwin incident report.")
    payload_incident = {
        "action": "update",
        "page": "incydenty",
        "id": skolwin_incident_id,
        "title": "MOVE04 Ruchy zwierząt (np. bobrów) nieopodal miasta Skolwin", # Keeping original ticket code
        "content": "Czujniki zarejestrowały szybko poruszające się obiekty, które zmierzały w kierunku rzeki. Przemieszczały się nieregularnie, co jest typowe dla zwierząt wodnych. Po kilku sekundach sygnał ustabilizował się i potwierdzono, że obiekty rzeczywiście znajdują się nad terenem w pobliżu Skolwina. W końcowej fazie ruchu obiekty wyrażnie zwolniły. Manewr nastąpił tuż przy rzece, zanim obiekty całkowicie zniknęły z radaru. Taki przebieg sugeruje aktywność zwierząt (np. bobrów) w tym rejonie. Nie udało się potwierdzić żródła sygnału ani jego dalszej trasy po utracie kontaktu."
    }
    send_to_centrala(payload_incident)

    # 3. Mark Skolwin Task as Done
    logger.info("Step 3: Marking Skolwin task as done.")
    payload_task = {
        "action": "update",
        "page": "zadania",
        "id": skolwin_task_id,
        "done": "YES",
        "content": "Zidentyfikowano zwierzęta (bobry), sprawa zamknięta."
    }
    send_to_centrala(payload_task)

    # 4. Create Komarowo Diversion
    logger.info("Step 4: Creating diversion incident for Komarowo.")
    payload_komarowo = {
        "action": "update",
        "page": "incydenty",
        "id": komarowo_incident_id,
        "title": "MOVE01 Wykrycie ruchu w okolicach miasta Komarowo",
        "content": "System wykrył wzmożoną aktywność ruchu  w rejonie niezamieszkałego miasta Komarowo sugerującą aktywność ludzi. Rekomendowana pilna obserwacja."

    }
    send_to_centrala(payload_komarowo)

    # 5. Finalize
    logger.info("Step 5: Finalizing the task.")
    payload_done = {
        "action": "done"
    }
    final_response = send_to_centrala(payload_done)
    
    logger.info(f"Final response from 'done' action: {final_response}")
    logger.info("--- Z0401 OKO Editor Solution Finished ---")

if __name__ == "__main__":
    solve_z0401()
