import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

import random
import requests
from apps.scraping.utils.proxy_manager import load_proxies

# Dynamically resolve the correct proxy file path
PROXY_PATH = os.path.join(os.path.dirname(__file__), "working_proxies_smoothcomp_com.csv")
PROXIES = load_proxies(proxy_file_path=PROXY_PATH)

def fetch_api_data(url, headers=None, timeout=10, verbose=False):
    proxies = PROXIES  # List of strings like "http://IP:PORT"
    random.shuffle(proxies)  # 💥 Randomize order once per call

    for proxy in proxies:
        proxy_config = {"http": proxy, "https": proxy}

        try:
            if verbose:
                print(f"🌐 Trying proxy: {proxy}")

            response = requests.get(url, headers=headers, proxies=proxy_config, timeout=timeout)
            if response.status_code == 200:
                if verbose:
                    print(f"✅ Success with proxy: {proxy}")
                return response

            if verbose:
                print(f"⚠️ Proxy returned status {response.status_code}: {proxy}")

        except requests.exceptions.RequestException as e:
            if verbose:
                print(f"[💥 Failed] {proxy} → {e}")

    print(f"❌ All proxies failed for URL: {url}")
    return None