#pagination_utils.py

import requests
from bs4 import BeautifulSoup
import urllib.parse

def get_max_pages(base_url):
    """Extracts the max number of pages from pagination navigation."""
    response = requests.get(base_url)
    
    if response.status_code != 200:
        print(f"⚠️ Failed to retrieve page. Status Code: {response.status_code}")
        return 1, None  # Default to 1 page if error occurs

    soup = BeautifulSoup(response.text, "html.parser")

    # Find pagination element
    pagination = soup.find("ul", class_="pagination")
    if not pagination:
        return 1, None  # No pagination, assume a single page

    # Identify pagination format
    max_page = 1
    pagination_url_format = None
    for link in pagination.find_all("a"):
        href = link.get("href")
        try:
            page_num = int(link.text.strip())
            max_page = max(max_page, page_num)
            if href and "?page=" in href:
                pagination_url_format = href.replace(str(page_num), "{page}")
        except ValueError:
            continue

    return max_page, pagination_url_format

def generate_paginated_urls(base_url):
    """Generates all paginated URLs dynamically."""
    max_pages, pagination_url_format = get_max_pages(base_url)

    if not max_pages:
        return []

    parsed_url = urllib.parse.urlparse(base_url)
    if not pagination_url_format:
        pagination_url_format = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?page={{page}}"

    return [pagination_url_format.format(page=page) for page in range(1, max_pages + 1)]
