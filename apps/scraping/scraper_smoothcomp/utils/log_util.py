from apps.scraping.scraper_smoothcomp.utils.directory import DirectoryManager
import csv
from typing import List

directory = DirectoryManager(__file__)

def log_failure(filename: str, data: dict, headers: List[str]):
    header_list = headers  # or use directly as "headers"

    log_path = directory.logs() / filename

    file_exists = log_path.exists()
    with log_path.open("a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header_list)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)
