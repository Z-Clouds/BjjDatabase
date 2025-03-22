import requests
import os
import json
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
from utils.pagination_utils import get_max_pages
# Function to scrape events
def scrape_events(event_host_id, event_host_name, test_mode=False):
    
    # Set up directories
    parent_dir = os.path.abspath(os.getcwd())
    data_dir = os.path.join(parent_dir, "data")
    raw_data_dir = os.path.join(data_dir, "raw")
    test_dir = os.path.join(data_dir, "test")

    # Create directories if they don't exist
    os.makedirs(raw_data_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)

    # Base URL
    base_url = f"https://adcc.smoothcomp.com/en/federation/{event_host_id}/events/past"
    output_file = os.path.join(raw_data_dir, f"{event_host_name}_events_detailed_{datetime.now().strftime('%Y-%m-%d')}.csv")
    test_output_file = os.path.join(test_dir, f"{event_host_name}_test_event_detail_{datetime.now().strftime('%Y-%m-%d')}.csv")

    # Get total pages
    max_pages = get_max_pages(base_url)
    print(f"Max pages: {max_pages}")

    # Define page range
    page_range = range(1, max_pages + 1) if not test_mode else range(1, 2)

    all_events = []
    unique_event_ids = set()

    for page in page_range:
        event_url =  f"{base_url}?page={page}"
        print(f"Fetching page {page} of {max_pages}: {event_url}")

        response = requests.get(event_url)
        if response.status_code != 200:
            print(f"Error {response.status_code} fetching page {page}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        # Find event data
        script_tag = None
        for script in soup.find_all("script"):
            if script.string and "var events =" in script.string:
                script_tag = script.string
                break

        if not script_tag:
            print(f"No event data found on page {page}. Check the extraction logic.")
            continue

        # Extract JSON and ensure each page contributes new data
        try:
            json_start = script_tag.find("var events =") + len("var events =")
            json_end = script_tag.find(";", json_start)
            events_json_text = script_tag[json_start:json_end].strip()
            events_data = json.loads(events_json_text)

            # Debugging: Confirm per-page extraction
            print(f"Page {page} extracted {len(events_data)} events.")

            # Append only truly new events
            new_events = [event for event in events_data if event["id"] not in unique_event_ids]
            unique_event_ids.update([event["id"] for event in new_events])
            all_events.extend(new_events)

            print(f"Page {page} added {len(new_events)} new events.")

        except json.JSONDecodeError as e:
            print(f"JSON Decoding Failed: {e}")
            print(f"Extracted JSON Text (First 500 chars):\n{events_json_text[:500]}")

    # Convert the full list of events to a DataFrame
    if all_events:
        df = pd.DataFrame(all_events)

        # Save to CSV
        df.to_csv(output_file, index=False)
        if test_mode:
            df.to_csv(test_output_file, index=False)
            print(f"[TEST MODE] Saved {len(df)} events to {test_output_file}")

        print(f"Successfully extracted and saved {len(df)} events to {output_file}")

    else:
        print("No events were extracted. Check the scraping logic or site changes.")
