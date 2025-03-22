import argparse
import logging
from SC_Event_Scraper import scrape_events
from SC_Event_Bracket_Bundle_Scraper import scrape_bracket_ids
from SC_Event_Bracket_Bundle_MatchID_Scraper import scrape_match_ids
from SC_MatchData_Scraper import scrape_match_data
from datetime import datetime
import os
import traceback

# ===============================
# 📜 set timestamp
# ===============================

date_stamp = datetime.now().strftime("%Y-%m-%d")

# ===============================
# 📜 SETUP LOGGING
# ===============================

log_file = os.path.join("logs", f"scrape_job{date_stamp}.log")
os.makedirs("logs", exist_ok=True)  # Ensure log directory exists

logging.basicConfig(
    filename=log_file,
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

def main(event_host_id, event_host_name, test_mode=False):
    test_check_text = "in production mode" if not test_mode else "in test mode"
    logging.info(f"🚀 Starting SmoothComp Scraper Job {test_check_text}...")
    print(f"🚀 Starting SmoothComp Scraper Job {test_check_text} ...")

    try:
        logging.info("📌 Step 1: Scraping Events  ...")
        print("📌 Step 1: Scraping Events...")
        scrape_events(event_host_id, event_host_name,test_mode)

        logging.info("📌 Step 2: Scraping Bracket IDs...")
        print("📌 Step 2: Scraping Bracket IDs from Api...")
        scrape_bracket_ids(event_host_name, test_mode)

        logging.info("📌 Step 3: Scraping Match IDs from Api...")
        print("📌 Step 3: Scraping Match IDs from Api...")
        scrape_match_ids(event_host_name, test_mode)

        
        logging.info("📌 Step 4: Scraping Match Data...")
        print("📌 Step 4: Scraping Match Data from Api...")
        scrape_match_data(event_host_name, test_mode)

        logging.info("✅ All Scraping Tasks Completed Successfully!")
        print("✅ All Scraping Tasks Completed Successfully!")

   
    except Exception as e:
        logging.error(f"❌ Error in scraping job: {e}\n{traceback.format_exc()}")
        print(f"❌ Error occurred: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run full event and match data scraping job.")
    parser.add_argument("--event_host_id", type=int, required=True, help="Event host ID (e.g., 176 for ADCC)")
    parser.add_argument("--event_host_name", type=str, required=True, help="Event host name (e.g., 'ADCC')")
    parser.add_argument("--test", action="store_true", help="Run a small test sample")

    args = parser.parse_args()
    main(args.event_host_id, args.event_host_name, args.test)
