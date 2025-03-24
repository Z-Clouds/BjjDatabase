import os
import random
import pandas as pd
from apps.scraping.utils.proxy_tester import test_proxies_and_save
from apps.scraping.scraper_smoothcomp.utils.directory import directory  # Ensure you have this import for directory handling

def load_match_ids(csv_file):
    """Load match IDs from the master match history CSV."""
    if not os.path.exists(csv_file):
        print(f"⚠️ Match ID file not found: {csv_file}")
        return []

    try:
        df = pd.read_csv(csv_file)
        if "match_id" not in df.columns:
            print("⚠️ CSV does not contain 'match_id' column. Check the file structure.")
            return []

        match_list = df["match_id"].dropna().astype(int).tolist()  # Ensure IDs are valid
        print(f"✅ Loaded {len(match_list)} match IDs from CSV.")
        return match_list
    except Exception as e:
        print(f"❌ Error loading match IDs: {e}")
        return []

def test_smooth_comp_proxies(
    max_threads=20,
    test_mode=False,
    verbose=False,
    include_socks=True
):
    """Test proxies against dynamically changing SmoothComp match URLs."""
    
    # Load past successful match IDs
    match_ids_file = directory.data() / "SC_master_match_ids_scraped.csv"
    match_ids = load_match_ids(match_ids_file)

    if not match_ids:
        print("❌ No match IDs available. Using fallback ID.")
        match_ids = [10445731]  # Default ID if no file exists

    # ✅ Define the base URL (without a fixed Match ID)
    base_url = "https://smoothcomp.com/en/getBracketMatchData"

    print(f"🔄 Loaded {len(match_ids)} Match IDs | Testing proxies against dynamic URLs")

    # Expand `~` to absolute paths
    csv_output_dir = os.path.expanduser("~/BjjDatabase/apps/scraping/scraper_smoothcomp/utils")
    log_output_dir = os.path.expanduser("~/BjjDatabase/logs")

    # ✅ Pass full match_ids list instead of single target_url
    test_proxies_and_save(
        match_ids=match_ids,  # 🔥 Pass the full list of match IDs
        base_url=base_url,    # 🔥 Pass the base URL (no Match ID yet)
        csv_output_dir=csv_output_dir,
        log_output_dir=log_output_dir,
        max_threads=max_threads,
        test_mode=test_mode,
        verbose=verbose,
        include_socks=include_socks
    )

if __name__ == "__main__":
    test_smooth_comp_proxies(test_mode=True, verbose=True)
