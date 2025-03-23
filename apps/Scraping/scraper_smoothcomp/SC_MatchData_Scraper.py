import requests
import os
import csv
import time
import random
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime 
from utils.fetch_api_utils import fetch_api_data
from utils.log_faileld_matchdata_extraction import log_failed_matchdata_extract

# ===============================
# 🔧 CONFIGURATION
# ===============================
THREADS = 5  # Number of concurrent threads
MAX_RETRIES = 3  # Retries for failed requests
DELAY_RANGE = (0.5, 2)  # Randomized delay range
date_stamp = datetime.now().strftime("%Y-%m-%d")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://smoothcomp.com",
}

parent_dir = os.path.abspath(os.getcwd())
data_dir = os.path.join(parent_dir, "data")
raw_data_dir = os.path.join(data_dir, "raw")
test_dir = os.path.join(data_dir, "test")

# ===============================
# 📂 LOAD EXISTING MATCH DATA
# ===============================
def load_existing_match_data(output_file):
    """Load existing match data to prevent duplicate API calls."""
    if not os.path.exists(output_file):
        return set()
    
    with open(output_file, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return {row["match_id"] for row in reader}

# ===============================
# 🔄 SCRAPE MATCH RESULTS
# ===============================
def scrape_match_data(event_host_name, test_mode=False):
    """Fetches new match result data, avoiding duplicates, and stores raw JSON."""
    input_file = f"data/raw/{event_host_name}_match_ids_{date_stamp}.csv"
    json_output_file = f"data/raw/{event_host_name}_match_data_raw_{date_stamp}.json"
    master_match_file = os.path.join(data_dir,f"SC_master_match_ids_scraped.csv")  # Stores all previous match IDs

    if not os.path.exists(input_file):
        print(f"❌ Match ID file {input_file} not found. Run match ID scraper first!")
        return

    os.makedirs("data/raw", exist_ok=True)

    # Load existing match IDs from previous scrapes
    existing_match_data = load_existing_match_data(master_match_file)

    match_results = []
    failed_matches = []

    def fetch_match_details(match):
        """Fetch match details and store raw JSON only if new."""
        match_id = match["match_id"]
        event_id = match["event_id"]

        # Skip if this match was already processed
        if match_id in existing_match_data:
            print(f"⚠️ Skipping already scraped match {match_id}")
            return

        url = f"https://smoothcomp.com/en/getBracketMatchData/{match_id}"

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                match_json = fetch_api_data(url, HEADERS, 10)
                 #failed request handling
                if match_json is None:
                    print(f"❌ {event_id} Bracket {match_id} failed attempts. Logging failure.")
                    log_failed_matchdata_extract(event_id, match_id)
                    continue  # Skip this bracket
                
                match_json["event_id"] = event_id
                match_json["match_id"] = match_id
                match_results.append(match_json)
                
                print(f"✅ Successfully fetched Match ID {match_id}") if not test_mode else print(match_json)
                return
            
            except (requests.RequestException, json.JSONDecodeError) as e:
                print(f"❌ Error fetching Match ID {match_id} (Attempt {attempt}): {e}")
                time.sleep(random.uniform(*DELAY_RANGE))

        failed_matches.append(match)

    # Read match IDs
    with open(input_file, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        match_list = list(reader)

    # **Test Mode Logic**: Sample only 10 matches
    if test_mode:
        match_list = match_list[:10]

    # Fetch match details concurrently
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        executor.map(fetch_match_details, match_list)

    # Save raw JSON data for later processing
    with open(json_output_file, mode="w", encoding="utf-8") as file:
        json.dump(match_results, file, indent=4)

    print(f"✅ Raw match data saved to {json_output_file}")


   # Append new match IDs to master match file **only if not in test mode**
    if match_results and not test_mode:
        with open(master_match_file, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if os.stat(master_match_file).st_size == 0:
                writer.writerow(["match_id"])  # Write header if file is empty
            for match in match_results:
                writer.writerow([match["match_id"]])

        print(f"✅ Updated master match file with {len(match_results)} new matches.")
    elif test_mode:
        print("⚠️ Test mode active. New matches were NOT added to the master match file.")