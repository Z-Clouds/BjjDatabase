import time
from apps.scraping.scraper_smoothcomp.utils.redis_util import (
    get_bracket_queue_size,
    get_match_queue_size,
    get_failed_brackets_count,
    get_failed_matches_count,
)

def display_queue_status():
    while True:
        print("\033c", end="")  # Clear terminal
        print("📦 REDIS QUEUE MONITOR\n")
        print(f"🧩 Bracket Queue:      {get_bracket_queue_size()} jobs")
        print(f"❌ Failed Brackets:    {get_failed_brackets_count()}")
        print()
        print(f"🎯 Match Queue:        {get_match_queue_size()} jobs")
        print(f"❌ Failed Matches:     {get_failed_matches_count()}")
        print("\nRefreshing every 3s...")
        time.sleep(3)

if __name__ == "__main__":
    display_queue_status()
