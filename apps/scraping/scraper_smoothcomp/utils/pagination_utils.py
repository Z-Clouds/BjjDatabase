#pagination_utils.py

import requests
from bs4 import BeautifulSoup

def get_max_pages(base_url):
    """Extracts the max number of pages from pagination navigation."""
    response = requests.get(base_url)
    
    if response.status_code != 200:
        print(f"⚠️ Failed to retrieve page. Status Code: {response.status_code}")
        return 1  # Default to 1 page if error occurs

    soup = BeautifulSoup(response.text, "html.parser")

    # Find pagination element
    pagination = soup.find("ul", class_="pagination")
    if not pagination:
        return 1  # No pagination, assume a single page

    # Identify maximum page number
    max_page = 1
    for link in pagination.find_all("a"):
        try:
            page_num = int(link.text.strip())
            max_page = max(max_page, page_num)
        except ValueError:
            continue

    return max_page