import csv
import requests
import json
from urllib.parse import urlparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse 

# 🔗 Static proxy API source
PROXY_API = "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=json"

# 🧪 Check if a proxy works with target site
def test_proxy(proxy_url, test_url):
    try:
        r = requests.get(test_url, proxies={"http": proxy_url, "https": proxy_url}, timeout=5)
        return r.status_code == 200
    except:
        return False

# 🧲 Fetch JSON-formatted proxy list
def get_proxies_from_api():
    try:
        response = requests.get(PROXY_API, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("proxies", [])
    except Exception as e:
        print("Proxy fetch failed:", e)
        return []

# 💥 Master function to test and save proxies
def test_proxies_and_save(target_url, max_threads=20):
    proxies = get_proxies_from_api()
    total = len(proxies)
    working_proxies = []

    print(f"⚙️ Starting proxy test against: {target_url}")
    start_time = datetime.now()

    with ThreadPoolExecutor(max_threads) as executor:
        future_to_proxy = {
            executor.submit(test_proxy, proxy["proxy"], target_url): proxy
            for proxy in proxies
        }

        for future in as_completed(future_to_proxy):
            proxy = future_to_proxy[future]
            if future.result():
                working_proxies.append(proxy)

    # 🔐 Output filename by target domain
    domain = urlparse(target_url).netloc.replace(".", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"working_proxies_{domain}.csv"
    log_filename = f"proxy_test_log_{domain}_{timestamp}.txt"

    # 💾 Save working proxies to CSV
    if working_proxies:
        with open(csv_filename, mode="w", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=working_proxies[0].keys())
            writer.writeheader()
            writer.writerows(working_proxies)
        print(f"✅ Saved {len(working_proxies)} working proxies to {csv_filename}")
    else:
        print("❌ No working proxies found.")

    # 📜 Write log
    with open(log_filename, "w") as log:
        log.write(f"🕐 Proxy Test Log\n")
        log.write(f"Started: {start_time}\n")
        log.write(f"Target URL: {target_url}\n")
        log.write(f"Total Proxies Tested: {total}\n")
        log.write(f"Working Proxies: {len(working_proxies)}\n")

    print(f"📄 Log saved to {log_filename}")

# 🧪 Entry point for CLI-style testing
#if __name__ == "__main__":
#    target = input("Enter the URL to test proxies against: ").strip()
#    test_proxies_and_save(target)
