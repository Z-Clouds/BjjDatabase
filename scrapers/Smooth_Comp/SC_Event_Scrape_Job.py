import argparse
import logging
import sys
import os
from datetime import datetime

# ✅ Import the actual scraper function
from SC_Event_Scraper import scrape_events

# ===============================
# 📜 SET UP LOGGING
# ===============================
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)  # Ensure log directory exists

log_filename = f"{log_dir}/scraper_{datetime.now().strftime('%Y-%m-%d')}.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ===============================
# 🏁 EXECUTE SCRAPER (REQUIRES ARGUMENTS)
# ===============================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape event data from SmoothComp.")
    parser.add_argument("--event_host_id", type=int, required=True, help="Event host ID (e.g., 176 for ADCC)")
    parser.add_argument("--event_host_name", type=str, required=True, help="Event host name (e.g., 'ADCC')")

    args = parser.parse_args()

    # ✅ Prevent running without required arguments
    if not args.event_host_id or not args.event_host_name:
        print("❌ ERROR: Both --event_host_id and --event_host_name are required.")
        logging.error("❌ Missing required arguments. Exiting.")
        sys.exit(1)

    logging.info(f"🚀 Starting scraper for {args.event_host_name} (ID: {args.event_host_id})")

    try:
        events = scrape_events(event_host_id=args.event_host_id, event_host_name=args.event_host_name)
        logging.info(f"✅ Successfully extracted {len(events)} total events.")
    except Exception as e:
        logging.error(f"❌ Error while running scraper: {e}")
        sys.exit(1)
