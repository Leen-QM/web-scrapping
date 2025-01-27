import time
import os
from scraper import scrape_bio_page  # Import the scrape function
from finalCrawling import crawl_page  # Existing crawling function

filename = 'countries_and_demonyms.csv'
start_time = time.time()

# Create a folder called "Mathaf Encyclopedia" if it doesn't already exist
folder_name = "Mathaf Encyclopedia"
os.makedirs(folder_name, exist_ok=True)

# Base URL of the website to crawl
base_url = "https://encyclopedia.mathaf.org.qa"
visited_urls = set()  # Set to store visited URLs
urls_to_visit = [base_url]  # List to store URLs to visit next
bio_urls = []  # List to store URLs with '/bios/Pages' in their path

crawl_first = True


if crawl_first:
    while urls_to_visit:
        current_url = urls_to_visit.pop(0)  # Dequeue the first URL

        if current_url in visited_urls:
            continue

        print(f"Crawling: {current_url}")

        # Use the crawl_page function to get new links from the page
        new_links = crawl_page(current_url)
        visited_urls.add(current_url)
        urls_to_visit.extend(new_links)

        # If the URL contains '/bios/Pages', add it to the bio_urls list
        if '/bios/Pages' in current_url:
            if 'init=' in current_url or 'default' in current_url:
                continue  # Skip URLs containing 'init='
            bio_urls.append(current_url)

    print(f"Crawling finished. Found {len(bio_urls)} bio pages.")
else:
    # If we don't crawl, just add the base URL to the bio_urls list directly
    bio_urls.append(base_url)


# Now scrape each bio page, extract entities, and generate word clouds
for bio_url in bio_urls:
    # Use the function from scraper.py
    scrape_bio_page(bio_url, folder_name)

# Execution time
end_time = time.time()
execution_time = end_time - start_time
print(f"\nExecution time: {execution_time} seconds")
