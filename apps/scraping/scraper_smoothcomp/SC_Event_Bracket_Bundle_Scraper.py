import requests
import pandas as pd
import os
import csv
from datetime import datetime
from utils.fetch_api_utils import fetch_api_data
from utils.log_failed_event_bracket_extract import log_failed_event_bracket_extract
import time
# ===============================
# 🛠️ CONFIGURATION
# ===============================

date_stamp = datetime.now().strftime("%Y-%m-%d")
HEADERS = {"User-Agent": "Mozilla/5.0"}

parent_dir = os.path.abspath(os.getcwd())
data_dir = os.path.join(parent_dir, "data")
raw_data_dir = os.path.join(data_dir, "raw")
test_dir = os.path.join(data_dir, "test")

successful_bracket_bundles_scraped_csv = os.path.join(data_dir, "successful_bracket_bundles_scraped_csv.csv")
failed_brackets_csv = os.path.join(data_dir, "failed_event_bracket_bundle_extractions.csv")

# ===============================
# 📂 LOAD TRACKING DATA
# ===============================

def load_completed_brackets():
    """Loads completed bracket scrapes safely, ensuring a proper CSV format."""
    if not os.path.exists(successful_bracket_bundles_scraped_csv):
        return set()

    completed_events = set()
    
    with open(successful_bracket_bundles_scraped_csv, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None or "event_id" not in reader.fieldnames:
            print("⚠️ Warning: `successful_bracket_bundles_scraped_csv.csv` is missing headers. Resetting file.")
            return set()

        for row in reader:
            if row.get("event_id"):
                completed_events.add(row["event_id"])

    return completed_events

def load_failed_brackets():
    """Loads failed bracket scrapes safely, ensuring a proper CSV format."""
    if not os.path.exists(failed_brackets_csv):
        return set()

    failed_events = set()
    
    with open(failed_brackets_csv, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None or "event_id" not in reader.fieldnames:
            print("⚠️ Warning: `failed_event_bracket_bundle_extractions.csv` is missing headers. Resetting file.")
            return set()

        for row in reader:
            if row.get("event_id"):
                failed_events.add(row["event_id"])

    return failed_events

def save_completed_bracket(event_id):
    """Appends an event ID to `successful_brackets.csv` with a header if missing."""
    file_exists = os.path.exists(successful_bracket_bundles_scraped_csv)
    
    with open(successful_bracket_bundles_scraped_csv, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists or os.stat(successful_bracket_bundles_scraped_csv).st_size == 0:
            writer.writerow(["event_id"])  
        writer.writerow([event_id])

# ===============================
# 🔎 SCRAPE BRACKET IDS
# ===============================

def scrape_bracket_ids(event_host_name, test_mode=False):
    """Scrapes bracket IDs while avoiding redundant processing."""

    completed_events = load_completed_brackets()
    failed_events = load_failed_brackets()
    event_csv_path = os.path.join(raw_data_dir, f"{event_host_name}_events_detailed_{date_stamp}.csv")

    if not os.path.exists(event_csv_path):
        print(f"❌ ERROR: Events CSV not found: {event_csv_path}")
        return

    events = pd.read_csv(event_csv_path)
    if "id" not in events.columns:
        print("❌ ERROR: 'id' column missing in events CSV.")
        return

    # Validate event IDs
    if events["id"].isnull().sum() > 0:
        print("⚠️ Warning: Some event IDs are missing! Check the event CSV.")
        events = events.dropna(subset=["id"])  

    event_ids = events["id"].astype(str).tolist()  
    if test_mode:
        event_ids = event_ids[:2]

    all_bracket_data = []

    for event_id in event_ids:
        if event_id in completed_events:
            print(f"⚠️ Skipping already processed event {event_id}")
            continue

        print(f"📡 Fetching Brackets for Event ID: {event_id}")
        bracket_api_url = f"https://adcc.smoothcomp.com/en/event/{event_id}/schedule/brackets.json"

        try:
            data = fetch_api_data(bracket_api_url, HEADERS)
            
            if data is None:
                print(f"⚠️ API calls failed logging failure:\n{data}")
                log_failed_event_bracket_extract(event_id)  # Save as failed
                continue  

            for bracket in data.get("brackets", []):
                all_bracket_data.append({
                    "event_id": event_id,
                    "bracket_bundle_id": bracket.get("bracket_bundle_id"),
                    "bracket_name": bracket.get("name"),
                })

            print(f"✅ Extracted {len(data.get('brackets', []))} brackets for event {event_id}")
            save_completed_bracket(event_id)  # Save as successful

        except requests.RequestException as e:
            print(f"❌ Error fetching bracket data for event {event_id}: {e}")
            log_failed_event_bracket_extract(event_id)
        time.sleep(1)
        
    bracket_bundle_csv_path = os.path.join(raw_data_dir, f"{event_host_name}_brackets_{date_stamp}.csv")

    if all_bracket_data:
        df_brackets = pd.DataFrame(all_bracket_data)
    else:
        df_brackets = pd.DataFrame(columns=["event_id", "bracket_bundle_id", "bracket_name"])  # Empty structure

    df_brackets.to_csv(bracket_bundle_csv_path, index=False)
    print(f"✅ Successfully ensured the brackets file exists: {bracket_bundle_csv_path}.")