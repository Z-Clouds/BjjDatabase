import csv
import random
import requests
from itertools import cycle

class ProxyPool:
    def __init__(self, proxy_csv_path, strategy="round_robin"):
        self.strategy = strategy
        self.proxies = self._load_proxies(proxy_csv_path)
        if not self.proxies:
            raise ValueError("No proxies loaded from file.")

        if strategy == "round_robin":
            self._proxy_cycle = cycle(self.proxies)

    def _load_proxies(self, path):
        proxies = []
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                proxy_url = row.get("proxy") or row.get("Proxy")
                if not proxy_url:
                    protocol = row.get("protocol")
                    ip = row.get("ip")
                    port = row.get("port")
                    if protocol and ip and port:
                        proxy_url = f"{protocol.strip()}://{ip.strip()}:{port.strip()}"
                if proxy_url:
                    proxies.append(proxy_url.strip())
        return proxies

    def get_proxy(self):
        if self.strategy == "round_robin":
            return next(self._proxy_cycle)
        elif self.strategy == "random":
            return random.choice(self.proxies)
        else:
            raise ValueError(f"Unsupported proxy rotation strategy: {self.strategy}")

    def get_session(self):
        proxy_url = self.get_proxy()
        session = requests.Session()
        session.proxies = {
            "http": proxy_url,
            "https": proxy_url
        }
        return session
