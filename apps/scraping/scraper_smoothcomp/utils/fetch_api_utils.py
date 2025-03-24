import requests
import random
import csv
from pathlib import Path

# Define proxy file path
PROXY_FILE = Path("/home/lordx/BjjDatabase/apps/scraping/scraper_smoothcomp/utils/working_proxies_smoothcomp_com.csv")

def load_proxies():
    """Loads proxies from CSV file."""
    proxies = []
    if PROXY_FILE.exists():
        with PROXY_FILE.open("r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header if it exists
            proxies = [row[0].strip() for row in reader if row]  # Extract first column (proxy)
    return proxies

def fetch_api_data(url, headers=None, timeout=10, verbose=False):
    """Fetches API data using proxies with failover handling."""
    
    proxies = load_proxies()  # Load proxies from file
    random.shuffle(proxies)  # Randomize order
    
    for proxy in proxies or [None]:  # Run at least once even if no proxies
        proxy_config = {"http": proxy, "https": proxy} if proxy else None

        try:
            if verbose:
                print(f"🌐 Trying URL: {url} | Using Proxy: {proxy or 'No Proxy'}")

            response = requests.get(url, headers=headers, proxies=proxy_config, timeout=timeout, allow_redirects=True)

            # 🔄 Detect Redirects
            if response.history:
                redirected_url = response.url
                if verbose:
                    print(f"🔄 Redirect detected → {redirected_url}")

                # 🔥 Always use the redirected base URL for future requests
                new_base_url = redirected_url.split("/en/")[0]
                corrected_url = f"{new_base_url}/en" + url.split("/en")[-1]

                if verbose:
                    print(f"🔄 Retrying with corrected base URL: {corrected_url}")

                response = requests.get(corrected_url, headers=headers, proxies=proxy_config, timeout=timeout)

            if response.status_code == 200:
                if verbose:
                    print(f"✅ Success: {url} | Proxy: {proxy or 'Direct Connection'}")
                return response

            if verbose:
                print(f"⚠️ Response {response.status_code}: {url}")

        except requests.exceptions.RequestException as e:
            if verbose:
                print(f"[💥 Failed] {url} → {e}")

    print(f"❌ All proxies failed for URL: {url}")
    return None
