import time
import os
from scrapper_v2 import fetch_main_content_advanced, process_bio_page  # Import the scrape function
from finalCrawling import crawl_page  # Existing crawling function


# Create a folder called "Mathaf Encyclopedia" if it doesn't already exist
'''folder_name = "Mathaf Encyclopedia"
os.makedirs(folder_name, exist_ok=True)'''

# Base URL of the website to crawl
'''base_url = "https://collections.qm.org.qa/"
visited_urls = set()  # Set to store visited URLs
urls_to_visit = [base_url]  # List to store URLs to visit next
bio_urls = []  # List to store URLs with '/bios/Pages' in their path

crawl_first = True

def crawl_and_extract_links(current_url):
    # Crawl the page and extract links
    new_links = crawl_page(current_url, session)
    
    # Filter out URLs already visited
    new_links = [link for link in new_links if link not in visited_urls]
    
    # Add the current URL to the visited set
    visited_urls.add(current_url)
    
    return new_links


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
        if '/objects/' in current_url:
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
'''

# Main script
if __name__ == "__main__":
    url = input("Enter the URL: ").strip()
    start_phrase = input("Enter the starting phrase: ").strip()
    end_phrase = input("Enter the ending phrase: ").strip()

    try:
        print("\nFetching content...")
        chunks = fetch_main_content_advanced(url, start_phrase, end_phrase)
        print("Content fetched successfully!")
        print(chunks)
        print("\nExtracting entities...")
        process_bio_page(url, chunks)

    except Exception as e:
        print(f"Error: {e}")
