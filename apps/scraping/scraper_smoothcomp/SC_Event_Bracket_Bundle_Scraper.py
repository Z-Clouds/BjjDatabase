import requests
import time
from datetime import datetime
from typing import List
import pandas as pd
import csv 

from apps.scraping.scraper_smoothcomp.utils.fetch_api_utils import fetch_api_data
from apps.scraping.scraper_smoothcomp.utils.redis_util import enqueue_bracket
from apps.scraping.scraper_smoothcomp.utils.log_util import log_failure
from apps.scraping.scraper_smoothcomp.utils.directory import directory

HEADERS = {"User-Agent": "Mozilla/5.0"}
DATESTAMP = datetime.now().strftime("%Y-%m-%d")

# Setup paths to store processing status
data_dir = directory.data()
successful_bracket_bundles_scraped_csv = data_dir / "successful_bracket_bundles_scraped_csv.csv"
failed_brackets_csv = data_dir / "failed_event_bracket_bundle_extractions.csv"

# ===============================
# 📂 LOAD TRACKING DATA
# ===============================
def load_completed_brackets():
    if not successful_bracket_bundles_scraped_csv.exists():
        return set()
    df = pd.read_csv(successful_bracket_bundles_scraped_csv)
    return set(df["event_id"].astype(str)) if "event_id" in df.columns else set()

def save_completed_bracket(event_id):
    file_exists = successful_bracket_bundles_scraped_csv.exists()
    with successful_bracket_bundles_scraped_csv.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists or successful_bracket_bundles_scraped_csv.stat().st_size == 0:
            writer.writerow(["event_id"])
        writer.writerow([event_id])

# ===============================
# 🔎 SCRAPE BRACKET IDS FOR GIVEN EVENTS
# ===============================
def scrape_bracket_ids(events: List[str], delay=1, test_mode=False):
    if not events:
        print("⚠️ No events provided to scrape_bracket_ids()")
        return

    completed_events = load_completed_brackets()

    for event in events[:2] if test_mode else events:
        event_id = str(event.get("id"))
        if not event_id:
            continue

        if event_id in completed_events:
            print(f"⚠️ Skipping already processed event {event_id}")
            continue

        print(f"📡 Fetching Brackets for Event ID: {event_id}")
        bracket_api_url = f"https://smoothcomp.com/en/event/{event_id}/schedule/brackets.json"

        try:
            resp = fetch_api_data(bracket_api_url, headers=HEADERS)

            if resp is None:
                print(f"❌ No response for event {event_id}")
                log_failure(
                    filename="failed_event_bracket_extractions.csv",
                    data={"event_id": event_id, "reason": "no_response", "timestamp": datetime.now().isoformat()},
                    headers=["event_id", "reason", "timestamp"]
                )
                continue

            try:
                data = resp.json()
            except Exception as e:
                print(f"💥 Failed to decode JSON for event {event_id}: {e}")
                log_failure(
                    filename="failed_event_bracket_extractions.csv",
                    data={"event_id": event_id, "reason": "json_error", "timestamp": datetime.now().isoformat()},
                    headers=["event_id", "reason", "timestamp"]
                )
                continue

            brackets = data.get("brackets", [])
            if not brackets:
                print(f"⚠️ No brackets found in JSON for event {event_id}")
                log_failure(
                    filename="failed_event_bracket_extractions.csv",
                    data={"event_id": event_id, "reason": "no_brackets", "timestamp": datetime.now().isoformat()},
                    headers=["event_id", "reason", "timestamp"]
                )
                continue

            for bracket in brackets:
                payload = {
                    "event_id": event_id,
                    "bracket_bundle_id": bracket.get("bracket_bundle_id"),
                    "bracket_name": bracket.get("name")
                }
                enqueue_bracket(payload)
                print(f"🧩 Queued bracket: {payload['bracket_bundle_id']} for event {event_id}")

            save_completed_bracket(event_id)
            print(f"✅ Processed {len(brackets)} brackets for event {event_id}")

        except requests.RequestException as e:
            print(f"❌ Network error fetching brackets for event {event_id}: {e}")
            log_failure(
                filename="failed_event_bracket_extractions.csv",
                data={"event_id": event_id, "reason": str(e), "timestamp": datetime.now().isoformat()},
                headers=["event_id", "reason", "timestamp"]
            )

        time.sleep(delay)