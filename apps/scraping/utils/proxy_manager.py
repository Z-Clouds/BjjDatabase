import os
import csv

def load_proxies(proxy_file_path=None):
    """
    Load proxies from a given CSV file path.
    If not provided, falls back to `working_proxies.csv` in the same folder as this script.
    """
    if proxy_file_path is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        proxy_file_path = os.path.join(current_dir, "working_proxies.csv")

    if not os.path.exists(proxy_file_path):
        raise FileNotFoundError(f"Proxy file not found at: {proxy_file_path}")

    proxies = []
    with open(proxy_file_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if "proxy" in row:
                proxies.append(row["proxy"])
    return proxies
