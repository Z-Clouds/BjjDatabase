import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import os
import argparse
from datetime import datetime

# ===============================
# 🛠️ CONFIGURATION
# ===============================

# Get the current date in YYYY-MM-DD format
date_stamp = datetime.now().strftime("%Y-%m-%d")

REQUEST_DELAY = (1, 3)  # Delay between requests to avoid overloading the server

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

# ===============================
# 🔎 EXTRACT MATCH DETAILS FROM PAGE
# ===============================
def scrape_bracket_ids(event_host_name, test_mode=False):
    """
    Extracts all bracket IDs from event pages.
    Saves the results to a CSV file.
    """

    # Load event IDs
    event_csv_path = os.path.join(raw_data_dir, f"{event_host_name}_events_detailed_{date_stamp}.csv")
    if not os.path.exists(event_csv_path):
        print(f"❌ ERROR: Events CSV not found: {event_csv_path}")
        return

    events = pd.read_csv(event_csv_path)
    
    if "id" not in events.columns:
        print("❌ ERROR: 'id' column missing in events CSV.")
        return
    
    event_ids = events["id"].tolist()
    if test_mode:
        event_ids = event_ids[:2]  # Limit to 2 events in test mode

    all_bracket_data = []

    for event_id in event_ids:
        bracket_api_url = f"https://adcc.smoothcomp.com/en/event/{event_id}/schedule/brackets.json"
        print(f"📡 Fetching Brackets for Event ID: {event_id}")

        try:
            response = requests.get(bracket_api_url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Extract bracket information
            for bracket in data.get("brackets", []):
                bracket_data = {
                    "event_id": event_id,
                    "bracket_bundle_id": bracket.get("bracket_bundle_id"),
                    "bracket_name": bracket.get("name"),
                    "bracket_group": bracket.get("group"),
                    "bracket_round": bracket.get("round"),
                    "registrations_count": bracket.get("registrations_count"),
                }
                all_bracket_data.append(bracket_data)

            print(f"✅ Extracted {len(data.get('brackets', []))} brackets for event {event_id}")

        except requests.RequestException as e:
            print(f"❌ Error fetching bracket data for event {event_id}: {e}")

    # Save to CSV
    if all_bracket_data:
        bracket_csv_path = os.path.join(raw_data_dir, f"{event_host_name}_brackets_{date_stamp}.csv")
        df_brackets = pd.DataFrame(all_bracket_data)
        df_brackets.to_csv(bracket_csv_path, index=False)
        print(f"✅ Successfully saved {len(df_brackets)} bracket IDs to {bracket_csv_path}")

    else:
        print("⚠️ No bracket IDs found.")

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
        response = requests.get(bracket_details_api_url, headers=HEADERS)
        data = response.json()
        
        try:
            response = requests.get(bracket_details_api_url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()

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
        
