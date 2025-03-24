import argparse
import json
import pandas as pd
import csv
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from redis import Redis

from apps.scraping.scraper_smoothcomp.utils.redis_util import (
    dequeue_match,
    log_failed_match
)
from apps.scraping.scraper_smoothcomp.utils.fetch_api_utils import fetch_api_data
from apps.scraping.scraper_smoothcomp.utils.directory import directory

# ===============================
# 🛠️ CONFIGURATION
# ===============================
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

redis = Redis()  # Assumes default localhost connection

# File paths
MATCH_IDS_FILE = directory.data() / "SC_master_match_ids_scraped.csv"
MATCHES_JSON_FILE = directory.raw() / "matches_raw.json"

# ✅ Cached Set of Processed Match IDs (Avoid Re-reading CSV Each Time)
_cached_processed_matches = None


# ===============================
# 📂 LOAD PROCESSED MATCHES (Only Once)
# ===============================
def load_processed_match_ids():
    """Loads the list of already processed match IDs from CSV and caches it."""
    global _cached_processed_matches
    if _cached_processed_matches is None:
        if not MATCH_IDS_FILE.exists():
            _cached_processed_matches = set()
        else:
            df = pd.read_csv(MATCH_IDS_FILE)
            _cached_processed_matches = set(df["match_id"].astype(str)) if "match_id" in df.columns else set()
    return _cached_processed_matches


# ===============================
# 📝 APPEND MATCH ID TO TRACKING FILE
# ===============================
def append_scraped_match_id(match_id):
    """Appends a processed match ID to the tracking CSV and updates cache."""
    global _cached_processed_matches
    file_exists = MATCH_IDS_FILE.exists()

    with MATCH_IDS_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["match_id"])  # Write header if file is new
        writer.writerow([match_id])

    # ✅ Update Cache to Avoid Re-reading CSV
    if _cached_processed_matches is not None:
        _cached_processed_matches.add(str(match_id))


# ===============================
# 📡 PROCESS MATCH JOB
# ===============================
def process_match_job(match_job):
    """Fetches and processes a match from the queue, saving it to JSON storage."""
    match_id = str(match_job.get("match_id"))  # Ensure string type
    event_id = match_job.get("event_id")  # Preserve Event ID

    # ✅ Skip if already processed
    if match_id in load_processed_match_ids():
        print(f"⚠️ Skipping already processed match: {match_id}")
        return

    print(f"\n🎯 Fetching Match ID: {match_id} (Event: {event_id})")
    url = f"https://smoothcomp.com/en/getBracketMatchData/{match_id}" # DO NOT CHANGE CHATGPT ASSHOLE

    try:
        response = fetch_api_data(url, HEADERS)
        if response is None:
            print(f"⚠️ Failed to fetch match {match_id}")
            log_failed_match(match_job)
            return

        json_data = response.json()  # ✅ Extract JSON from Response object

        # ✅ Embed Event ID into the match data
        json_data["event_id"] = event_id

        # ✅ Ensure `matches_raw.json` exists & append match data
        existing_data = []
        if MATCHES_JSON_FILE.exists():
            try:
                with MATCHES_JSON_FILE.open("r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                    if not isinstance(existing_data, list):
                        existing_data = []  # Ensure it's a list
            except json.JSONDecodeError:
                existing_data = []  # Handle invalid JSON

        existing_data.append(json_data)  # Append new match

        # ✅ Write back updated data
        with MATCHES_JSON_FILE.open("w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)

        # ✅ Append Match ID to Master List
        append_scraped_match_id(match_id)

        print(f"✅ Appended match {match_id} to {MATCHES_JSON_FILE} with Event ID: {event_id}")
        print(f"📌 Added Match ID {match_id} to Master List")

    except json.JSONDecodeError as e:
        print(f"💥 JSON Decode Error for match {match_id}: {e}\n📡 Full Response: {response.text}")
        log_failed_match(match_job)
    except Exception as e:
        print(f"❌ Exception for match {match_id}: {e}")
        log_failed_match(match_job)


# ===============================
# 🚀 START WORKER POOL W/ TIMEOUT
# ===============================
def start_match_worker_pool(max_workers=20, loop_delay=0.25, idle_timeout=600):
    """Starts a pool of match workers to process jobs from Redis."""
    print(f"🚀 Starting {max_workers} match worker threads with idle timeout: {idle_timeout} sec...\n")
    last_work_time = time.time()
    loop_count = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        while True:
            match_job = dequeue_match()

            if match_job:
                executor.submit(process_match_job, match_job)
                last_work_time = time.time()
            else:
                idle_duration = time.time() - last_work_time
                if idle_duration > idle_timeout:
                    print(f"💤 No match jobs for {idle_timeout} seconds. Shutting down worker pool.")
                    break

            loop_count += 1
            if loop_count % 20 == 0:
                try:
                    size = redis.llen("match_queue")
                    print(f"📦 Redis match queue size: {size}")
                except Exception as e:
                    print(f"⚠️ Could not read Redis queue size: {e}")

            time.sleep(loop_delay)


# ===============================
# 🚀 TEST MODE: PROCESS ONE MATCH JOB & CHECK QUEUE
# ===============================
def test_single_match_job():
    print("\n🎯 [TEST MODE] Processing ONE match job from queue...\n")

    match_job = dequeue_match()

    if not match_job:
        print("⏳ No match jobs in queue.")
        return

    process_match_job(match_job)

    # 📊 Check Match Queue After Processing
    match_queue_size = redis.llen("match_queue")
    print(f"\n📦 Match Queue Size After Test: {match_queue_size} jobs")


# ===============================
# 🔥 CLI ENTRY POINT
# ===============================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Match Worker with Test Mode")
    parser.add_argument("--test", action="store_true", help="Run in test mode (process one match job)")
    args = parser.parse_args()

    if args.test:
        test_single_match_job()
    else:
        start_match_worker_pool()
