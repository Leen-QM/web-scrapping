import re  # Import regular expressions
from gliner import GLiNER
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

start_time = time.time()

# Initialize GLiNER with the base model
model = GLiNER.from_pretrained("urchade/gliner_multi-v2.1")

# Define labels for entity prediction
labels = ["Person", "Country", "Date", "Place", "City"]

# Predefined list of common pronouns (case-insensitive)
pronoun_list = {"he", "she", "him", "her", "it", "they", "them", "we", "us", "i", "me", "you", "his", "their", "our"}

# Function to extract entities from biography content
def extract_entities(biography_content):
    all_entities = []
    for chunk in biography_content:
        entities = model.predict_entities(chunk, labels, threshold=0.5)
        all_entities.extend(entities)

    # Categorize entities into separate groups for better distinction
    human_names = set()
    countries = set()
    dates = set()
    places = set()
    cities = set()

    for entity in all_entities:
        label = entity["label"]
        text = entity["text"].strip()

        # Normalize text to lowercase for comparison
        text_lower = text.lower()

        # Add to appropriate category, filtering out pronouns from human names
        if label == "Person" and text_lower not in pronoun_list:
            human_names.add(text)
        elif label == "Country":
            countries.add(text)
        elif label == "Date":
            # Extract year if present in full date
            match = re.search(r'\b(18|19|20)\d{2}\b', text)
            if match:
                dates.add(match.group(0))  # Add the year only
        elif label == "Place":
            places.add(text)
        elif label == "City":
            cities.add(text)

    # Sort entities for display
    sorted_human_names = sorted(human_names)  # Alphabetical
    sorted_countries = sorted(countries)  # Alphabetical
    sorted_dates = sorted(dates, key=int)  # Numerical order (years only)
    sorted_places = sorted(places)  # Alphabetical
    sorted_cities = sorted(cities)  # Alphabetical

    return sorted_human_names, sorted_countries, sorted_dates, sorted_places, sorted_cities

# Function to crawl a page and extract links
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

# Base URL of the website to crawl
base_url = "https://encyclopedia.mathaf.org.qa/"
visited_urls = set()  # Set to store visited URLs
urls_to_visit = [base_url]  # List to store URLs to visit next
bio_urls = []  # List to store URLs with '/bio' in their path

# Crawl the website and collect bio URLs
while urls_to_visit:
    current_url = urls_to_visit.pop(0)  # Dequeue the first URL

    if current_url in visited_urls:
        continue

    print(f"Crawling: {current_url}")

    new_links = crawl_page(current_url)
    visited_urls.add(current_url)
    urls_to_visit.extend(new_links)

      # If the URL contains '/bios/Pages', add it to the bio_urls list
    if '/bios/Pages' in current_url:
        if 'init=' in current_url:
            continue  # Skip URLs containing 'init='
        bio_urls.append(current_url)

print(f"Crawling finished. Found {len(bio_urls)} bio pages.")

# Now scrape each bio page and extract named entities
for bio_url in bio_urls:
    print(f"Scraping bio page: {bio_url}")
    response = requests.get(bio_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the Biography and Exhibitions headers
    biography_h1 = soup.find('h1', string=lambda text: text and 'biography' in text.lower())
    exhibitions_h1 = soup.find('h1', string=lambda text: text and 'exhibitions' in text.lower())

    biography_content = []

    # Check if both headers are found
    if biography_h1 and exhibitions_h1:
        # Find the content between 'Biography' and 'Exhibitions'
        for sibling in biography_h1.find_next_siblings():
            # Stop when the Exhibitions header is encountered
            if sibling == exhibitions_h1:
                break
            if sibling.name == 'p':  # Only collect <p> tags
                biography_content.append(sibling.get_text(strip=True))

    # Extract named entities from biography content
    human_names, countries, dates, places, cities = extract_entities(biography_content)

    # Display categorized entities
    print("\nHuman Names (Alphabetical):")
    print(human_names)

    print("\nCountries (Alphabetical):")
    print(countries)

    print("\nDates (Years Only, Increasing Order):")
    print(dates)

    print("\nPlaces (Alphabetical):")
    print(places)

    print("\nCities (Alphabetical):")
    print(cities)

# Execution time
end_time = time.time()
execution_time = end_time - start_time
print(f"\nExecution time: {execution_time} seconds")
