import time
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from apps.scraping.scraper_smoothcomp.utils.redis_util import dequeue_match, log_failed_match
from apps.scraping.scraper_smoothcomp.utils.fetch_api_utils import fetch_api_data
from apps.scraping.scraper_smoothcomp.utils.directory import directory
from redis import Redis

# ===============================
# 🛠️ CONFIGURATION
# ===============================
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

date_stamp = datetime.now().strftime("%Y-%m-%d")
data_dir = directory.custom("data/matches")
redis = Redis()  # Assumes default localhost connection — update if needed

# ===============================
# 🧠 PROCESS MATCH JOB
# ===============================
def process_match_job(match_job):
    match_id = match_job.get("match_id")
    event_id = match_job.get("event_id")
    bracket_id = match_job.get("bracket_id")

    print(f"\n🎯 Fetching Match ID: {match_id} (Event: {event_id}, Bracket: {bracket_id})")
    url = f"https://www.smoothcomp.com/en/match/{match_id}/getData"

    try:
        data = fetch_api_data(url, HEADERS)
        if data is None:
            print(f"⚠️ Failed to fetch match {match_id}")
            log_failed_match(match_job)
            return

        output_path = data_dir / f"match_{match_id}_.json"
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ Saved match data → {output_path}")

    except Exception as e:
        print(f"❌ Exception for match {match_id}: {e}")
        log_failed_match(match_job)

# ===============================
# 🚀 START WORKER POOL W/ TIMEOUT
# ===============================
def start_match_worker_pool(max_workers=5, loop_delay=0.25, idle_timeout=600):
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

            # Periodically show queue size
            loop_count += 1
            if loop_count % 20 == 0:  # every ~5 seconds (0.25 * 20)
                try:
                    size = redis.llen("match_queue")
                    print(f"📦 Redis match queue size: {size}")
                except Exception as e:
                    print(f"⚠️ Could not read Redis queue size: {e}")

            time.sleep(loop_delay)
