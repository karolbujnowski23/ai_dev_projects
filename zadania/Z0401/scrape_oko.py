import os
import requests
import re
from src.config import APIKEY

def clean_html(html_content):
    # This function now only cleans HTML, structured parsing is separate
    content = re.sub(r'<style.*?>.*?</style>', '', html_content, flags=re.DOTALL)
    content = re.sub(r'<script.*?>.*?</script>', '', content, flags=re.DOTALL)
    content = re.sub(r'<[^>]+>', ' ', content)
    content = re.sub(r'\s+', ' ', content).strip()
    return content

def parse_skolwin_item(block):
    """Parses a single HTML block for Skolwin-related details and returns structured data."""
    item_details = {}
    
    # Extract ID from the main link's href (assuming 32-char hex ID)
    id_match = re.search(r'href="/[^/]+/([a-f0-9]{32})"', block)
    if id_match:
        item_details['id'] = id_match.group(1)

    # Extract Title from strong tag
    title_match = re.search(r'<strong>(.*?)</strong>', block, re.DOTALL)
    if title_match:
        item_details['title'] = title_match.group(1).strip()
    
    # Extract all tags and statuses (text from elements with class="metric...")
    all_tags = []
    metric_tags = re.findall(r'class="metric[^>]*>([^<]+)<', block)
    for tag in metric_tags:
        cleaned_tag = tag.strip()
        if cleaned_tag:
            all_tags.append(cleaned_tag)
    item_details['tags'] = all_tags
    
    return item_details

def run():
    print("Starting hybrid scraper for OKO system...")
    s = requests.Session()
    
    print("Logging in...")
    login_data = {
        "action": "login",
        "login": "Zofia",
        "password": "Zofia2026!",
        "access_key": APIKEY
    }
    s.post("https://oko.ag3nts.org/", data=login_data)
    
    urls_to_scrape = [
        "https://oko.ag3nts.org/",          # Incidents page
        "https://oko.ag3nts.org/zadania"     # Tasks page
    ]
    
    all_collected_data = []
    
    for url in urls_to_scrape:
        print(f"Scraping page: {url}")
        r = s.get(url)
        r.raise_for_status()
        html_content = r.text

        # Add general cleaned content for context
        all_collected_data.append(f"--- RAW CLEANED CONTENT FROM: {url} ---")
        all_collected_data.append(clean_html(html_content))
        all_collected_data.append("\n") # Separator

        # Now, specifically look for Skolwin items and extract structured data
        item_blocks = [m.group(0) for m in re.finditer(r'(?:<a[^>]*href="/[^/]+/[a-f0-9]{32}"[^>]*>\s*)?<article class="list-item[^>]*>.*?</article>', html_content, re.DOTALL)]
        skolwin_found = False
        for block in item_blocks:
            if "Skolwin" in block:
                skolwin_found = True
                item_details = parse_skolwin_item(block)
                all_collected_data.append("--- STRUCTURED SKOLWIN DATA ---")
                all_collected_data.append(f"  Source URL: {url}")
                # BUG FIX: Changed 'item.get' to 'item_details.get'
                all_collected_data.append(f"  ID: {item_details.get('id', 'Not Found')}")
                all_collected_data.append(f"  Title: {item_details.get('title', 'Not Found')}")
                all_collected_data.append(f"  Tags: {item_details.get('tags', [])}")
                all_collected_data.append("\n") # Separator
        
        if not skolwin_found and "skolwin" in clean_html(html_content).lower():
             all_collected_data.append("--- GENERAL SKOLWIN MENTION (NO STRUCTURED ITEM) ---")
             all_collected_data.append(f"  Found 'Skolwin' mention on {url}, but not in a structured item.")
             all_collected_data.append("\n")

    final_content = "\n".join(all_collected_data)
    
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scraped_data.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_content)
        
    print(f"Web scraping complete. Mixed data saved to {output_path}.")

if __name__ == "__main__":
    run()