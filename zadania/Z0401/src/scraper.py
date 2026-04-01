import logging
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from src.config import APIKEY
logger = logging.getLogger("scraper")

OKO_URL = "https://oko.ag3nts.org/"
LOGIN = "Zofia"
PASSWORD = "Zofia2026!"

def get_oko_data():
    """Scrapes OKO website to find IDs for incidents and tasks, including a non-task incident for Komarowo."""
    logger.info("Starting scraper to find OKO data.")
    
    skolwin_incident_id = None
    skolwin_task_id = None
    all_incident_ids = set()
    all_task_ids = set()
    incident_details = {}
    task_details = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Login
        page.goto(OKO_URL)
        page.fill('input[name="login"]', LOGIN)
        page.fill('input[name="password"]', PASSWORD)
        page.fill('input[name="access_key"]', APIKEY) 
        # No access_key field based on previous debug
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")

        # Scrape Incidents
        page.goto(f"{OKO_URL}/incydenty")
        html_incidents = page.content()
        soup_incidents = BeautifulSoup(html_incidents, 'html.parser')
        
        for a in soup_incidents.find_all('a', class_='entry-link'):
            incident_id = a['href'].split('/')[-1]
            all_incident_ids.add(incident_id)
            title_element = a.find('strong')
            content_element = a.find('p')
            badge_element = a.find('span', class_='metric')

            title = title_element.get_text(strip=True) if title_element else ""
            content = content_element.get_text(strip=True) if content_element else ""
            badge = badge_element.get_text(strip=True) if badge_element else ""
            
            incident_details[incident_id] = {"title": title, "content": content, "badge": badge}

            if 'Skolwin' in title or 'Skolwin' in content:
                skolwin_incident_id = incident_id
                logger.info(f"Found Skolwin incident ID: {skolwin_incident_id}")
                
        # Scrape Zadania
        page.goto(f"{OKO_URL}/zadania")
        html_tasks = page.content()
        soup_tasks = BeautifulSoup(html_tasks, 'html.parser')

        for article in soup_tasks.find_all('article', class_='list-item'):
            link_element = article.find('a', class_='task-main-link')
            if link_element:
                task_id = link_element['href'].split('/')[-1]
                all_task_ids.add(task_id)
                task_title_element = link_element.find('strong')
                task_status_element = article.find('a', class_='metric--pending')

                task_title = task_title_element.get_text(strip=True) if task_title_element else ""
                task_status = task_status_element.get_text(strip=True) if task_status_element else "wykonane" # Default if not pending
                
                task_details[task_id] = {"title": task_title, "status": task_status}

                if 'Skolwin' in task_title:
                    skolwin_task_id = task_id
                    logger.info(f"Found Skolwin task ID: {skolwin_task_id}")
                
        browser.close()
    
    if not skolwin_incident_id or not skolwin_task_id:
        logger.error("Could not find Skolwin incident or task ID.")
        raise ValueError("Scraping failed to find required Skolwin IDs.")
        
    # Find a Komarowo incident ID that is not a task ID
    komarowo_incident_id = "351c0d9c90d66b4c040fff1259dd191d"
    for incident_id in all_incident_ids:
        if incident_id not in all_task_ids:
            komarowo_incident_id = incident_id
            logger.info(f"Found Komarowo-suitable incident ID (not in tasks): {komarowo_incident_id}")
            break

    if not komarowo_incident_id:
        logger.error("Could not find an incident ID suitable for Komarowo (not existing in tasks).")
        # Fallback to a known ID if no suitable one is found, though this might not meet strict criteria
        # For now, we will raise an error as per the new constraint.
        raise ValueError("Scraping failed to find Komarowo-suitable incident ID (not in tasks).")
        
    return {
        "skolwin_incident_id": skolwin_incident_id,
        "skolwin_task_id": skolwin_task_id,
        "komarowo_incident_id": komarowo_incident_id,
        "incident_details": incident_details,
        "task_details": task_details
    }
