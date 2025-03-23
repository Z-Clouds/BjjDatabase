import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

# URL of the past events page

url = "https://adcc.smoothcomp.com/en/federation/176/events/past?page{}"

# Get the page content
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Find the script containing "var events ="
script_tag = None
for script in soup.find_all("script"):
    if script.string and "var events =" in script.string:
        script_tag = script.string
        break

if not script_tag:
    print("❌ No event data found. Check the extraction logic.")
else:
    # Extract the JSON-like data from within the script
    try:
        json_start = script_tag.find("var events =") + len("var events =")
        json_end = script_tag.find(";", json_start)
        events_json_text = script_tag[json_start:json_end].strip()

        # Parse the JSON
        events_data = json.loads(events_json_text)

        # Convert to DataFrame
        df = pd.DataFrame(events_data)

        # Save to CSV
        df.to_csv("adcc_events_detailed.csv", index=False)
        print("✅ Successfully extracted and saved event data.")

    except json.JSONDecodeError as e:
        print(f"❌ JSON Decoding Failed: {e}")
        print(f"🔍 Extracted JSON Text (First 500 chars):\n{events_json_text[:500]}")
