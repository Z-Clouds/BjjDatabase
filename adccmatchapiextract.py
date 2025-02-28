import requests
import pandas as pd
import time
import random
import json
from concurrent.futures import ThreadPoolExecutor

# Configuration
MATCH_IDS_CSV = "match_ids.csv"  # Input: List of match IDs
OUTPUT_CSV = "match_data.csv"  # Output: Fetched match details
FAILED_CSV = "failed_matches.csv"  # Stores failed API requests
THREADS = 5  # Number of concurrent threads (Adjust for speed vs. safety)
MAX_RETRIES = 3  # Retries for failed requests
DELAY_RANGE = (0.5, 2)  # Randomized delay range (seconds)

# Headers to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://smoothcomp.com",
}

# Read match IDs from CSV
df = pd.read_csv(MATCH_IDS_CSV)
matches = df.to_dict(orient="records")  # Convert to list of dicts

# Storage for results
match_data = []
failed_matches = []

def fetch_match_details(match):
    """
    Fetches match details from SmoothComp API.
    Includes retry logic & adaptive delay to avoid detection.
    """
    event_id = match["event_id"]
    event_name = match["event_name"]
    match_id = match["match_id"]

    url = f"https://smoothcomp.com/en/getBracketMatchData/{match_id}"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)

            # Handle rate limits or failures
            if response.status_code == 429:  # Too many requests
                wait_time = random.uniform(5, 10)
                print(f"⏳ Rate limited! Waiting {wait_time:.2f}s before retrying...")
                time.sleep(wait_time)
                continue
            elif response.status_code != 200:
                print(f"⚠️ Failed (Attempt {attempt}): {url} | Status: {response.status_code}")
                time.sleep(random.uniform(*DELAY_RANGE))
                continue
            
            # Parse JSON response
            match_json = response.json()
            match_json["event_id"] = event_id
            match_json["event_name"] = event_name
            match_json["match_id"] = match_id

            # Save the data
            match_data.append(match_json)
            print(f"✅ Successfully fetched Match ID {match_id} from Event {event_name}")
            return
        
        except (requests.RequestException, json.JSONDecodeError) as e:
            print(f"❌ Error fetching Match ID {match_id} (Attempt {attempt}): {e}")
            time.sleep(random.uniform(*DELAY_RANGE))

    # If all retries fail, store the failed match for later reattempt
    print(f"❌ Max retries reached. Storing Match ID {match_id} for later.")
    failed_matches.append(match)

# Run the scraper with threading for speed
with ThreadPoolExecutor(max_workers=THREADS) as executor:
    executor.map(fetch_match_details, matches)

# Save successful match data to CSV
df_matches = pd.DataFrame(match_data)
df_matches.to_csv(OUTPUT_CSV, index=False)
print(f"\n✅ Successfully saved {len(match_data)} matches to {OUTPUT_CSV}.")

# Save failed matches for later retry
if failed_matches:
    df_failed = pd.DataFrame(failed_matches)
    df_failed.to_csv(FAILED_CSV, index=False)
    print(f"⚠️ {len(failed_matches)} matches failed. Saved to {FAILED_CSV} for later retries.")
