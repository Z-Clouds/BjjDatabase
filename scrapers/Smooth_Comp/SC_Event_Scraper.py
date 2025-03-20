from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import re
import time
import json
import sys
import os

# ✅ Fix: Dynamically add the project root to sys.path
current_file_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_file_path, ".."))  # Adjust path based on depth
sys.path.append(project_root)

# ✅ Now import the utility
from utils.pagination_utils import generate_paginated_urls


# Now import utils
from utils.pagination_utils import generate_paginated_urls


# ===============================
# 🛠️ SETUP SELENIUM DRIVER
# ===============================
def setup_driver():
    """Configures and returns a headless Selenium WebDriver."""
    options = Options()
    options.add_argument("--headless")  # Run without opening a window
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

# ===============================
# 📝 EXTRACT EVENT JSON TEXT
# ===============================
def extract_event_text(page_source):
    """Extracts the JSON event text from the page source using regex."""
    
    # Try capturing a JSON array anywhere in the page
    match = re.search(r'(\[\{.*?\}\])', page_source, re.DOTALL)
    
    if match:
        events_text = match.group(1).strip()
        print("✅ Successfully extracted event data!")
        
        # Validate JSON format
        try:
            json.loads(events_text)
            return events_text
        except json.JSONDecodeError:
            print("⚠️ Extracted data is not valid JSON!")
            return None
    else:
        print("⚠️ No JSON found! Regex might need adjustment.")
        return None

# ===============================
# 🔄 SCRAPE EVENTS FOR ANY HOST
# ===============================
def scrape_events(event_host_id, event_host_name):
    """
    Scrapes all events for a given host from SmoothComp.
    
    :param event_host_id: ID of the event host (e.g., 176 for ADCC).
    :param event_host_name: Name of the event host for file naming.
    :return: List of extracted event data.
    """

    base_url = f"https://smoothcomp.com/en/federation/{event_host_id}/events/past"
    driver = setup_driver()
    
    # ✅ Use pagination utility to get all page URLs
    paginated_urls = generate_paginated_urls(base_url)
    print(f"🔄 Found {len(paginated_urls)} pages to scrape.")

    all_events = []

    for page_num, page_url in enumerate(paginated_urls, start=1):
        print(f"📄 Fetching page {page_num} of {len(paginated_urls)}: {page_url}")

        driver.get(page_url)
        time.sleep(5)  # Allow JavaScript to load fully

        # ✅ Debug - Confirm we are on the correct page
        print(f"🔍 Current Page URL: {driver.current_url}")

        event_text = extract_event_text(driver.page_source)
        if event_text:
            try:
                events_json = json.loads(event_text)
                all_events.extend(events_json)
                print(f"✅ Extracted {len(events_json)} events from page {page_num}")
            except json.JSONDecodeError:
                print(f"⚠️ Failed to parse JSON on page {page_num}")

    driver.quit()

    # ✅ Save results
    events_file = f"data/{event_host_name}_events.json"
    if all_events:
        os.makedirs("data", exist_ok=True)
        with open(events_file, "w", encoding="utf-8") as f:
            json.dump(all_events, f, indent=4)
        print(f"✅ Saved {len(all_events)} events to {events_file}")

    return all_events

# ===============================
# 🏁 EXECUTE SCRAPER
# ===============================
if __name__ == "__main__":
    events = scrape_events(event_host_id=176, event_host_name="ADCC")
    print(f"Extracted {len(events)} total events.")
