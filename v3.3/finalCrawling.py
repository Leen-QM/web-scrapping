import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


# Function to crawl a page and extract links
def crawl_page(url, visited_urls,url_path):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        soup = BeautifulSoup(response.content, "html.parser")

        # Extract links and enqueue new URLs
        links = []
        for link in soup.find_all("a", href=True):
            # Check if the link contains '/bios/Pages/' and is not already visited
            if url_path in link["href"] and link["href"] not in visited_urls:
                next_url = urljoin(url, link["href"])
                links.append(next_url)

        return links

    except requests.exceptions.RequestException as e:
        print(f"Error crawling {url}: {e}")
        return []

# Function to crawl and extract links from the website, and return bio URLs
def crawl_and_extract_links(base_url, website_type, url_path):
    visited_urls = set()  # Set to store visited URLs
    urls_to_visit = [base_url]  # List to store URLs to visit next
    bio_urls = []  # List to store URLs with '/bios/Pages/' in their path
    if website_type == 1:
        url_path = "/objects/"
    elif website_type == 2:
        url_path = "/bios/Pages/"

    while urls_to_visit:
        current_url = urls_to_visit.pop(0)  # Dequeue the first URL

        if current_url in visited_urls:
            continue

        print(f"Crawling: {current_url}")

        # Use the crawl_page function to get new links from the page
        new_links = crawl_page(current_url, visited_urls,url_path)
        visited_urls.add(current_url)
        urls_to_visit.extend(new_links)

        # If the URL contains '/bios/Pages/', add it to the bio_urls list
        if url_path in current_url:
            if 'init=' in current_url or 'default' in current_url:
                continue  # Skip URLs containing 'init='
            bio_urls.append(current_url)

    return bio_urls
