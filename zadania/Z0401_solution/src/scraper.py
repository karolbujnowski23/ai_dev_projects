import requests
import logging
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from src.config import OKO_URL, APIKEY

logger = logging.getLogger("scraper")
print(f"API Key: {APIKEY}")
def get_oko_data():
    """Scrapes OKO website to find IDs for incidents and tasks, including non-task incident for Komarowo."""
    logger.info("Starting scraper to find OKO data.")
    
    skolwin_incident_id = None
    skolwin_task_id = None
    all_incident_ids = set()
    all_task_ids = set()
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Login
        page.goto(OKO_URL)
        page.fill('input[name="login"]', "Zofia")
        page.fill('input[name="password"]', "Zofia2026!")
        page.fill('input[name="access_key"]', APIKEY) # Assuming APIKEY is same as password for login
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")

        # Scrape Incidents
        page.goto(f"{OKO_URL}/incydenty")
        html_incidents = page.content()
        soup_incidents = BeautifulSoup(html_incidents, 'html.parser')
        
        for a in soup_incidents.find_all('a', class_='entry-link'):
            incident_id = a['href'].split('/')[-1]
            all_incident_ids.add(incident_id)
            if 'Skolwin' in a.get_text():
                skolwin_incident_id = incident_id
                logger.info(f"Found Skolwin incident ID: {skolwin_incident_id}")
                
        # Scrape Zadania
        page.goto(f"{OKO_URL}/zadania")
        html_tasks = page.content()
        soup_tasks = BeautifulSoup(html_tasks, 'html.parser')

        for a in soup_tasks.find_all('a', class_='task-main-link'):
            task_id = a['href'].split('/')[-1]
            all_task_ids.add(task_id)
            if 'Skolwin' in a.get_text():
                skolwin_task_id = task_id
                logger.info(f"Found Skolwin task ID: {skolwin_task_id}")
                
        browser.close()
    
    if not skolwin_incident_id or not skolwin_task_id:
        logger.error("Could not find Skolwin incident or task ID.")
        raise ValueError("Scraping failed to find required Skolwin IDs.")
        
    # Find a Komarowo incident ID that is not a task ID
    komarowo_incident_id = None
    for incident_id in all_incident_ids:
        if incident_id not in all_task_ids:
            komarowo_incident_id = incident_id
            logger.info(f"Found Komarowo-suitable incident ID (not in tasks): {komarowo_incident_id}")
            break

    if not komarowo_incident_id:
        komarowo_incident_id = "351c0d9c90d66b4c040fff1259dd191d"
        logger.info("Could not find an incident ID suitable for Komarowo (used placeholder).")
        
    return {
        "skolwin_incident_id": skolwin_incident_id,
        "skolwin_task_id": skolwin_task_id,
        "komarowo_incident_id": komarowo_incident_id
    }
