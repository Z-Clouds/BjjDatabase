import requests
import pandas as pd
from bs4 import BeautifulSoup
import time

# Configuration
MATCHLIST_CSV = "matchlist_urls.csv"  # CSV file containing matchlist page URLs
OUTPUT_CSV = "match_ids.csv"  # Where to store extracted match IDs
LIMIT = None  # Limit number of URLs to process for testing

# Headers to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://smoothcomp.com",
}

# Read matchlist URLs from CSV
df = pd.read_csv(MATCHLIST_CSV)
matchlist_urls = df["Matchlist URL"].tolist()[:LIMIT]  # Apply test limit

all_matches = []

def extract_match_ids(url):
    """
    Extracts match IDs along with event details from a matchlist page.
    """
    print(f"📄 Scraping matchlist page: {url}")

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"⚠️ Failed to fetch page. Status: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract event ID from URL (e.g., https://adcc.smoothcomp.com/en/event/19885/schedule/matchlist -> 19885)
        event_id = url.split("/event/")[1].split("/")[0]

        # Extract event name (if available)
        event_name_tag = soup.find("h1")
        event_name = event_name_tag.text.strip() if event_name_tag else f"Event_{event_id}"

        # Find match elements
        match_elements = soup.find_all("div", class_="match-row")
        match_data = []

        for match in match_elements:
            # Extract match ID from the data-target attribute (e.g., collapse10431344 -> 10431344)
            data_target = match.get("data-target")
            if data_target and "collapse" in data_target:
                match_id = data_target.replace("collapse", "").strip().lstrip(".")  # Remove leading dot

                match_data.append({
                    "event_id": event_id,
                    "event_name": event_name,
                    "match_id": match_id
                })

        print(f"✅ Found {len(match_data)} matches for Event {event_id} - {event_name}.")
        return match_data

    except requests.RequestException as e:
        print(f"❌ Error fetching matchlist: {e}")
        return []

# Loop through each matchlist URL
for url in matchlist_urls:
    match_info = extract_match_ids(url)
    all_matches.extend(match_info)
    time.sleep(1)  # Avoid hitting request limits

# Save match IDs with event details to CSV
df_match_ids = pd.DataFrame(all_matches, columns=["event_id", "event_name", "match_id"])
df_match_ids.to_csv(OUTPUT_CSV, index=False)

print(f"\n✅ Successfully saved {len(all_matches)} match IDs to {OUTPUT_CSV}.")
