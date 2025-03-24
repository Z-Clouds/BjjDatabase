import json
import pandas as pd

from bs4 import BeautifulSoup
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from apps.scraping.scraper_smoothcomp.utils.pagination_utils import get_max_pages
from apps.scraping.scraper_smoothcomp.utils.fetch_api_utils import fetch_api_data
from apps.scraping.scraper_smoothcomp.utils.directory import directory
from apps.scraping.scraper_smoothcomp.utils.log_util import log_failure

ALL_EVENTS_URL = "https://smoothcomp.com/en/events/past?cg=1,7,4,3,24"
DATESTAMP = datetime.now().strftime("%Y-%m-%d")
HEADERS = {"User-Agent": "Mozilla/5.0"}

output_file = directory.raw() / f"all_events_detailed_{DATESTAMP}.csv"
test_output_file = directory.test() / f"test_event_detail_{DATESTAMP}.csv"
def scrape_event_pages(test_mode=False, max_workers=5):
    max_pages = get_max_pages(ALL_EVENTS_URL)
    print(f"🔍 Found {max_pages} pages of past events")

    page_range = range(1, 3) if test_mode else range(1, max_pages + 1)

    def scrape_page(page):
        url = f"{ALL_EVENTS_URL}&page={page}"
        print(f"📄 Scraping page {page}: {url}")
        resp = fetch_api_data(url, headers=HEADERS, verbose=False)

        if not resp:
            log_failure("event_scrape_errors.csv", {"page": page, "url": url}, headers=["page", "url"])
            return []

        return extract_events_from_html(resp.text)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(scrape_page, page): page for page in page_range}
        for future in as_completed(futures):
            page = futures[future]
            try:
                events = future.result()
                if events:
                    print(f"✅ Page {page}: {len(events)} events")
                    yield events
                else:
                    print(f"⚠️ Page {page}: no events returned")

            except Exception as e:
                print(f"💥 Thread error on page {page}: {e}")

def extract_events_from_html(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    script_tag = next((s for s in soup.find_all("script") if s.string and "var events =" in s.string), None)

    if not script_tag:
        return []

    try:
        start = script_tag.string.find("var events =") + len("var events =")
        end = script_tag.string.find(";", start)
        json_str = script_tag.string[start:end].strip()
        return json.loads(json_str)
    except Exception as e:
        print(f"💥 Error extracting events from HTML: {e}")
        return []

def save_events_to_csv(event_batches, is_test=False):
    all_events = [event for batch in event_batches for event in batch]
    df = pd.DataFrame(all_events)
    df.to_csv(output_file, index=False)
    print(f"📁 Saved {len(df)} total events → {output_file}")

    if is_test:
        df.to_csv(test_output_file, index=False)
        print(f"[TEST MODE] Also saved → {test_output_file}")
