import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import os
from datetime import datetime
import random
from utils.fetch_api_utils import fetch_api_data
from utils.log_failed_bracket_bundle_match_extract import log_failed_bracket_match_extract
# ===============================
# 🛠️ CONFIGURATION
# ===============================

# Get the current date in YYYY-MM-DD format
date_stamp = datetime.now().strftime("%Y-%m-%d")

# Headers to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://smoothcomp.com",
}

# Directory Setup
parent_dir = os.path.abspath(os.getcwd())
data_dir = os.path.join(parent_dir, "data")
raw_data_dir = os.path.join(data_dir, "raw")
test_dir = os.path.join(data_dir, "test")
successful_bracket_match_extract_csv = os.path.join(data_dir, "successful_bracket_match_extract_csv.csv")
failed_bracket_match_extract_csv = os.path.join(data_dir, "failed_bracket_match_extract_csv.csv")

def scrape_match_ids(event_host_name, test_mode=False):
    """
    Extracts all match IDs from brackets using API calls.
    Saves the match IDs to a CSV file.
    """

    # Load bracket CSV
    bracket_csv_path = os.path.join(raw_data_dir, f"{event_host_name}_brackets_{date_stamp}.csv")
    if not os.path.exists(bracket_csv_path):
        print(f"❌ ERROR: Brackets CSV not found: {bracket_csv_path}")
        return

    df_brackets = pd.read_csv(bracket_csv_path)
    
    if "event_id" not in df_brackets.columns or "bracket_bundle_id" not in df_brackets.columns:
        print("❌ ERROR: CSV missing 'event_id' or 'bracket_bundle_id' column.")
        return

    # Limit to 2 brackets in test mode
    if test_mode:
        df_brackets = df_brackets.head(2)

    all_matches = []

    for index, row in df_brackets.iterrows():
        event_id = row["event_id"]
        bracket_id = row["bracket_bundle_id"]
        bracket_details_api_url = f"https://adcc.smoothcomp.com/en/event/{event_id}/schedule/new/bracket.json/bundle/{bracket_id}"
        print(f"📡 Fetching Matches for Event {event_id}, Bracket {bracket_id}")
        
        try:
            data = fetch_api_data(bracket_details_api_url, HEADERS)
            #failed request handling
            if data is None:
                print(f"❌ {event_id} Bracket {bracket_id} failed attempts. Logging failure.")
                log_failed_bracket_match_extract(event_id, bracket_id)
                continue  # Skip this bracket
            # Extract match IDs
            matches = data.get("matches", [])
            for match in matches:
                match_info = {
                    "event_id": event_id,
                    "bracket_bundle_id": bracket_id,
                    "match_id": match["id"]
                }
                all_matches.append(match_info)

            print(f"✅ Extracted {len(matches)} matches from Bracket bundle {bracket_id}")

        except requests.RequestException as e:
            print(f"❌ Error fetching match data for event {event_id}, bracket bundle {bracket_id}: {e}")

    # Save to CSV
    if all_matches:
        match_csv_path = os.path.join(raw_data_dir, f"{event_host_name}_match_ids_{date_stamp}.csv")
        df_matches = pd.DataFrame(all_matches)
        df_matches.to_csv(match_csv_path, index=False)
        print(f"✅ Successfully saved {len(df_matches)} match IDs to {match_csv_path}")

    else:
        print("⚠️ No match IDs found.")
        
