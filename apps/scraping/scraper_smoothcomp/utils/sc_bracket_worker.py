import time
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json 

from apps.scraping.scraper_smoothcomp.utils.redis_util import (
    dequeue_bracket,
    enqueue_match,
    log_failed_bracket
)
from apps.scraping.scraper_smoothcomp.utils.fetch_api_utils import fetch_api_data
from redis import Redis

# ===============================
# 🛠️ CONFIGURATION
# ===============================
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

redis = Redis()  # Adjust if you're using a custom Redis setup

# ===============================
# 🧠 PROCESS BRACKET JOB
# ===============================
def process_bracket_job(bracket_job):
    if not bracket_job:
        print("⏳ No bracket job provided.")
        return

    event_id = bracket_job.get("event_id")
    bracket_id = bracket_job.get("bracket_bundle_id")

    print(f"\n📡 Processing Bracket: {bracket_id} (Event: {event_id})")

    api_url = f"https://www.smoothcomp.com/en/event/{event_id}/schedule/new/bracket.json/bundle/{bracket_id}"
    print(f"🌐 Fetching URL: {api_url}")

    try:
        response = fetch_api_data(api_url, headers=HEADERS)
        
        if response is None:
            print(f"❌ API request failed for {api_url}")
            log_failed_bracket(bracket_job)
            return
        
        # Debugging: Print response headers
        #print(f"📡 Response Headers: {response.headers}")
        #print(f"📡 Response URL (after redirects): {response.url}")

        # Debug Response Content
        try:
            data = response.json()
            # print(f"📡 API Response JSON (First 500 chars): {json.dumps(data, indent=2)[:500]}...")
        except json.JSONDecodeError as e:
            # print(f"💥 JSON Decode Error: {e}\n📡 Full Response Text: {response.text}")
            log_failed_bracket(bracket_job)
            return

        if "matches" not in data or not data["matches"]:
            print(f"⚠️ No matches found in response for bracket {bracket_id}.")
            log_failed_bracket(bracket_job)
            return

        match_count = 0
        for match in data["matches"]:
            match_payload = {
                "event_id": event_id,
                "bracket_bundle_id": bracket_id,
                "match_id": match.get("id")
            }
            enqueue_match(match_payload)
            match_count += 1

        print(f"✅ Queued {match_count} matches from Bracket {bracket_id}")

    except Exception as e:
        print(f"❌ Exception while processing bracket {bracket_id}: {e}")
        log_failed_bracket(bracket_job)


# ===============================
# 🚀 START WORKER POOL W/ TIMEOUT
# ===============================
def start_bracket_worker_pool(max_workers=20, loop_delay=0.25, idle_timeout=600):
    print(f"🚀 Starting {max_workers} bracket worker threads with idle timeout: {idle_timeout} sec...\n")
    last_work_time = time.time()
    loop_count = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        while True:
            bracket_job = dequeue_bracket()

            if bracket_job:
                executor.submit(process_bracket_job, bracket_job)
                last_work_time = time.time()
            else:
                idle_duration = time.time() - last_work_time
                if idle_duration > idle_timeout:
                    print(f"💤 No bracket jobs for {idle_timeout} seconds. Shutting down worker pool.")
                    break

            loop_count += 1
            if loop_count % 20 == 0:
                try:
                    size = redis.llen("bracket_queue")
                    print(f"📦 Redis bracket queue size: {size}")
                except Exception as e:
                    print(f"⚠️ Could not read Redis queue size: {e}")

            time.sleep(loop_delay)

# ===============================
# 🚀 TEST MODE: PROCESS ONE BRACKET JOB & CHECK MATCH QUEUE
# ===============================
def test_single_bracket_job():
    print("\n🎯 [TEST MODE] Processing ONE bracket job from queue...\n")

    bracket_job = dequeue_bracket()

    if not bracket_job:
        print("⏳ No bracket jobs in queue.")
        return

    process_bracket_job(bracket_job)

    # 📊 Check Match Queue After Processing
    match_queue_size = redis.llen("match_queue")
    print(f"\n📦 Match Queue Size: {match_queue_size} jobs")

# ===============================
# 🔥 CLI ENTRY POINT
# ===============================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bracket Worker with Test Mode")
    parser.add_argument("--test", action="store_true", help="Run in test mode (process one bracket job)")
    args = parser.parse_args()

    if args.test:
        test_single_bracket_job()
    else:
        start_bracket_worker_pool()
