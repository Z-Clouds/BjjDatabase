import csv
import requests
import os
import random
import sys
import threading

from urllib.parse import urlparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


# SOCKS support
try:
    import socks
    HAS_SOCKS = True
except ImportError:
    HAS_SOCKS = False

# Proxy sources
PROXY_SOURCES = [
    {
        "url": "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=json",
        "type": "proxyscrape"
    },
    {
        "url": "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
        "type": "text",
        "default_protocol": "http"
    },
    {
        "url": "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc",
        "type": "geonode"
    }
]

# ===========================
# 🏗 Fetch Proxies (Multi-threaded)
# ===========================
def fetch_proxies_from_source(source):
    """Fetch proxies from a given source."""
    try:
        response = requests.get(source["url"], timeout=10)
        response.raise_for_status()

        if source["type"] == "proxyscrape":
            return response.json().get("proxies", [])

        elif source["type"] == "text":
            return [f"{source['default_protocol']}://{p.strip()}" for p in response.text.strip().split("\n") if p.strip()]

        elif source["type"] == "geonode":
            data = response.json()
            proxies = []
            for item in data.get("data", []):
                ip = item.get("ip")
                port = item.get("port")
                protocols = item.get("protocols", [])
                for protocol in protocols:
                    proxies.append(f"{protocol}://{ip}:{port}")
            return proxies

    except Exception as e:
        print(f"⚠️ Failed to fetch proxies from {source['url']}: {e}")
        return []

def fetch_proxies():
    """Fetch proxies from all sources concurrently."""
    all_proxies = []
    with ThreadPoolExecutor(max_workers=len(PROXY_SOURCES)) as executor:
        future_to_source = {executor.submit(fetch_proxies_from_source, src): src for src in PROXY_SOURCES}
        for future in as_completed(future_to_source):
            all_proxies.extend(future.result())

    print(f"✅ Fetched {len(all_proxies)} total proxies.")
    return all_proxies

# ===========================
# 🚀 Test Proxies (Multi-threaded)
# ===========================


def test_proxy(proxy_url, match_ids, base_url, lock, writer, writer_file, stats, verbose):
    """Test if a proxy works against a random match URL and update the progress ticker."""
    import random  # Ensures random.choice works inside threads
    
    # Pick a new match ID for every request
    match_id = random.choice(match_ids)
    test_url = f"{base_url}/{match_id}"

    try:
        response = requests.get(test_url, proxies={"http": proxy_url, "https": proxy_url}, timeout=5)

        if response.status_code == 200:
            with lock:
                writer.writerow({"proxy": proxy_url})
                writer_file.flush()
                stats["success"] += 1
            if verbose:
                print(f"[✔️] Proxy working: {proxy_url}")

        else:
            with lock:
                stats["failed"] += 1  # Update failed counter

    except Exception:
        with lock:
            stats["failed"] += 1  # Update failed counter

    finally:
        with lock:
            stats["tested"] += 1  # Update tested counter
            print(f"\r🧪 Testing Proxies | ✅ {stats['success']} | ❌ {stats['failed']} | 🔄 {stats['tested']}", end="", flush=True)


# ===========================
# 🎯 Master Function: Fetch & Test (Now Fully Threaded)
# ===========================
def test_proxies_and_save(match_ids, base_url, csv_output_dir=None, log_output_dir=None, max_threads=20, test_mode=False, verbose=False, include_socks=True):
    """Fetch, test, and save working proxies (Fully Multi-Threaded)."""
    proxies = fetch_proxies()

    if not include_socks:
        proxies = [p for p in proxies if not p.startswith("socks")]
        
    if not proxies:
        print("❌ No proxies retrieved.")
        return

    if test_mode:
        proxies = proxies[:10]

    total = len(proxies)
    print(f"\n🔍 Starting proxy test | Total Proxies: {total}")

    stats = {"tested": 0, "success": 0, "failed": 0}
    lock = threading.Lock()

    csv_output_dir = os.path.abspath(os.path.expanduser(csv_output_dir or os.getcwd()))
    log_output_dir = os.path.abspath(os.path.expanduser(log_output_dir or os.path.join(os.getcwd(), "logs")))

    os.makedirs(csv_output_dir, exist_ok=True)
    os.makedirs(log_output_dir, exist_ok=True)

    csv_path = os.path.join(csv_output_dir, "working_proxies.csv")

    # ✅ Test proxies with progress ticker
    with open(csv_path, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["proxy"])
        writer.writeheader()

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = {
                executor.submit(test_proxy, proxy, match_ids, base_url, lock, writer, f, stats, verbose): proxy for proxy in proxies
            }

            for _ in as_completed(futures):
                pass  # We process each completed thread here

    print(f"\n✅ Proxy Testing Complete!")
    print(f"📊 Final Results: ✅ {stats['success']} | ❌ {stats['failed']} | 🔄 {stats['tested']}")

