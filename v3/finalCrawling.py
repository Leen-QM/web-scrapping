import requests
import requests_cache  # Import requests-cache
from bs4 import BeautifulSoup;
from urllib.parse import urljoin


# Initialize requests-cache with a cache file
requests_cache.install_cache('web_cache', expire_after=604800)  # Cache expires after 1 week

# Function to crawl a page and extract links (now using cached requests)
def crawl_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        soup = BeautifulSoup(response.content, "html.parser")

        # Extract links and enqueue new URLs
        links = []
        for link in soup.find_all("a", href=True):
            if '/bios/Pages' in link["href"]:
                next_url = urljoin(url, link["href"])
                links.append(next_url)

        return links

    except requests.exceptions.RequestException as e:
        print(f"Error crawling {url}: {e}")
        return []

