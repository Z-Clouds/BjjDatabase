import pandas as pd
from SmoothCompScrapers.AdccOpen.Scripts.pagination_utils import generate_paginated_urls

# Load event data (replace with actual file path if needed)
events_df = pd.read_csv("adcc_events_detailed.csv")

# Create matchlist URLs based on event ID
base_matchlist_urls = [f"{url}/schedule/matchlist" for url in events_df["url"]]

# Generate paginated matchlist URLs
all_matchlist_pages = []
for base_url in base_matchlist_urls:
    paginated_urls = generate_paginated_urls(base_url)
    all_matchlist_pages.extend(paginated_urls)

# Save matchlist URLs to CSV
matchlist_df = pd.DataFrame({"Matchlist URL": all_matchlist_pages})
matchlist_df.to_csv("matchlist_urls.csv", index=False)

print("\n📂 Matchlist URLs saved to 'matchlist_urls.csv'.")
print(matchlist_df)