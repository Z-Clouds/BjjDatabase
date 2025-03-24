import argparse
import logging
import os
import traceback
from datetime import datetime

from apps.scraping.scraper_smoothcomp.SC_Event_Scraper import scrape_event_pages
from apps.scraping.scraper_smoothcomp.SC_Event_Bracket_Bundle_Scraper import scrape_bracket_ids
from apps.scraping.scraper_smoothcomp.utils.sc_bracket_worker import start_bracket_worker_pool
from apps.scraping.scraper_smoothcomp.utils.sc_match_worker import start_match_worker_pool
from apps.scraping.scraper_smoothcomp.utils.directory import DirectoryManager
from apps.scraping.scraper_smoothcomp.utils.smooth_comp_proxy_tester import test_smooth_comp_proxies

# ===============================
# 📜 SETUP LOGGING
# ===============================

directory = DirectoryManager(__file__)
raw_data_dir = directory.raw()
test_dir = directory.test()

date_stamp = datetime.now().strftime("%Y-%m-%d")
log_file = os.path.join("logs", f"scrape_job_{date_stamp}.log")
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename=log_file,
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# ===============================
# 🚀 MASTER SCRAPER ORCHESTRATOR
# ===============================
def main(test_mode=False, skip_proxy_test=False):
    test_msg = "[TEST MODE]" if test_mode else "[PRODUCTION MODE]"
    logging.info(f"🚀 Starting SmoothComp Scraper Job {test_msg}")
    print(f"🚀 Starting SmoothComp Scraper Job {test_msg}")

    try:
        # 📌 Step 0: Proxy Testing
        if not skip_proxy_test:
            logging.info("📌 Step 0: Testing proxies")
            print("📌 Step 0: Testing proxies")
            test_smooth_comp_proxies(
                max_threads=20,
                test_mode=test_mode,
                verbose=True
            )
        else:
            logging.info("⚠️ Proxy testing skipped via --skip-proxy-test flag")
            print("⚠️ Proxy testing skipped")

        # 📌 Step 1: Start Bracket Worker (queues match jobs)
        logging.info("📌 Step 2: Scraping match IDs (bracket worker)")
        print("📌 Step 2: Scraping match IDs (bracket worker)")
        start_bracket_worker_pool(max_workers=10, idle_timeout=600)

        # 📌 Step 2: Start Match Worker
        logging.info("📌 Step 3: Scraping match data (match worker)")
        print("📌 Step 3: Scraping match data (match worker)")
        start_match_worker_pool(max_workers=10, idle_timeout=600)

        # 📌 Step 3: Scrape Events and Stream to Bracket Scraper
        logging.info("📌 Step 1: Scraping events and queuing brackets")
        print("📌 Step 1: Scraping events and queuing brackets")
        for event_batch in scrape_event_pages(test_mode=test_mode, max_workers=10):
            scrape_bracket_ids(event_batch, test_mode=test_mode)

        logging.info("✅ All scraping steps completed successfully!")
        print("✅ All scraping steps completed successfully!")

    except Exception as e:
        logging.error(f"❌ Scraper encountered an error: {e}\n{traceback.format_exc()}")
        print(f"❌ Scraper encountered an error: {e}")

# ===============================
# 🧪 ENTRY POINT
# ===============================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SmoothComp Scraping Orchestrator")
    parser.add_argument("--test", action="store_true", help="Run in test mode with limited data")
    parser.add_argument("--skip-proxy-test", action="store_true", help="Skip proxy testing step")

    args = parser.parse_args()
    main(test_mode=args.test, skip_proxy_test=args.skip_proxy_test)
