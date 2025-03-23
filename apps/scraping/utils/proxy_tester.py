import csv
import requests
import os
from urllib.parse import urlparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from threading import Lock

# SOCKS support
try:
    import socks
    HAS_SOCKS = True
except ImportError:
    HAS_SOCKS = False

# Static proxy API source
PROXY_API = "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=json"

# Check if a proxy works with target site
def test_proxy(proxy_url, test_url, lock, writer, writer_file, row, stats, verbose):
    try:
        r = requests.get(test_url, proxies={"http": proxy_url, "https": proxy_url}, timeout=5)
        if r.status_code == 200:
            with lock:
                writer.writerow(row)
                writer_file.flush()
                stats["success"] += 1
            if verbose:
                print(f"[\u2705] Proxy working: {proxy_url}")
        else:
            if verbose:
                print(f"[\u274C] Proxy failed (bad status): {proxy_url}")
    except Exception as e:
        if verbose:
            print(f"[\U0001F4A5] Proxy failed: {proxy_url} | Error: {e}")
    finally:
        with lock:
            stats["tested"] += 1
            if verbose:
                print(f"Tested: {stats['tested']} / Success: {stats['success']}")

# Fetch proxy list from API
def get_proxies_from_api():
    try:
        response = requests.get(PROXY_API, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("proxies", [])
    except Exception as e:
        print("Proxy fetch failed:", e)
        return []

# Master function to test and save proxies
def test_proxies_and_save(target_url, csv_output_dir=None, log_output_dir=None, max_threads=20, test_mode=False, verbose=False, include_socks=True):
    proxies = get_proxies_from_api()
    if not proxies:
        print("No proxies retrieved.")
        return

    if not include_socks:
        proxies = [p for p in proxies if not p["protocol"].lower().startswith("socks")]
    elif not HAS_SOCKS:
        proxies = [p for p in proxies if not p["protocol"].lower().startswith("socks")]
        print("[!] SOCKS support not available. Skipping SOCKS proxies.")

    if test_mode:
        proxies = proxies[:10]

    total = len(proxies)
    print(f"\u2699\ufe0f Starting proxy test against: {target_url} | Total to test: {total}")
    start_time = datetime.now()

    domain = urlparse(target_url).netloc.replace(".", "_")
    timestamp = start_time.strftime("%Y%m%d_%H%M%S")

    csv_output_dir = os.path.abspath(os.path.expanduser(csv_output_dir or os.getcwd()))
    log_output_dir = os.path.abspath(os.path.expanduser(log_output_dir or os.path.join(os.getcwd(), "logs")))

    os.makedirs(csv_output_dir, exist_ok=True)
    os.makedirs(log_output_dir, exist_ok=True)

    csv_path = os.path.join(csv_output_dir, f"working_proxies_{domain}.csv")
    log_path = os.path.join(log_output_dir, f"proxy_test_log_{domain}_{timestamp}.txt")

    stats = {"tested": 0, "success": 0}
    lock = threading.Lock()

    with open(csv_path, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=proxies[0].keys())
        writer.writeheader()

        with ThreadPoolExecutor(max_threads) as executor:
            futures = [
                executor.submit(
                    test_proxy,
                    proxy["proxy"],
                    target_url,
                    lock,
                    writer,
                    f,
                    proxy,
                    stats,
                    verbose
                ) for proxy in proxies
            ]
            for _ in as_completed(futures):
                pass

    with open(log_path, "w") as log:
        log.write("\U0001F552 Proxy Test Log\n")
        log.write(f"Started: {start_time}\n")
        log.write(f"Target URL: {target_url}\n")
        log.write(f"Total Proxies Tested: {stats['tested']}\n")
        log.write(f"Working Proxies: {stats['success']}\n")
        log.write(f"Working proxies saved to: {csv_path}\n")

    print(f"\u2705 Working proxies saved to: {csv_path}")
    print(f"\U0001F4C4 Log saved to: {log_path}")
