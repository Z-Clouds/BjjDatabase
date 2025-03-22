import requests
import time
import random
import json

# Configuration
MAX_RETRIES = 3
DELAY_RANGE = (1, 3)  # Delay between retries

def fetch_api_data(url, HEADERS):
    """
    Handles API requests with retries, error handling, and rate limit handling.
    Returns parsed JSON response or None if all attempts fail.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)

            if response.status_code == 429:  # Rate limit handling
                print(f"⏳ Rate limited! Retrying after delay... ({attempt}/{MAX_RETRIES})")
                time.sleep(random.uniform(5, 10))  # Longer delay for rate limits
                continue

            if response.status_code != 200:
                print(f"⚠️ Failed (Attempt {attempt}): {url} | Status: {response.status_code}")
                time.sleep(random.uniform(*DELAY_RANGE))
                continue

            if not response.text.strip():  # Empty response check
                print(f"⚠️ Warning: Empty response for {url}. Retrying...")
                time.sleep(random.uniform(2, 5))
                continue

            try:
                return response.json()  # Parse JSON response
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON from {url}. Retrying...")
                time.sleep(random.uniform(2, 5))
                continue

        except requests.RequestException as e:
            print(f"❌ Request failed (Attempt {attempt}): {e}")
            time.sleep(random.uniform(*DELAY_RANGE))

    print(f"❌ All attempts failed for {url}. Returning None.")
    return None  # If all retries fail, return None
