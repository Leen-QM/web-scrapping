import re  # Import regular expressions
import csv 
from finalMapping import is_it_a_nationality
from finalWordCloud import generate_word_cloud  
from gliner import GLiNER
import time
import requests
from bs4 import BeautifulSoup
from collections import Counter
from urllib.parse import urljoin
import os  # Import os for folder creation
from PIL import Image  # Import the Image module from PIL (Python Imaging Library)


start_time = time.time()

# GLiNER with the base model
model = GLiNER.from_pretrained("urchade/gliner_multi-v2.1")

# entity prediction labels
labels = ["Person", "Country", "Date", "Place", "City"]

# Predefined list of common pronouns (case-insensitive)
pronoun_list = {"he", "she", "him", "her", "it", "they", "them", "we", "us", "i", "me", "you", "his", "their", "our"}

# Create a folder called "Mathaf Encyclopedia" if it doesn't already exist
folder_name = "Mathaf Encyclopedia"
os.makedirs(folder_name, exist_ok=True)

# Function to extract entities from biography content
def extract_entities(biography_content):
    all_entities = []
    for chunk in biography_content:
        entities = model.predict_entities(chunk, labels, threshold=0.5)
        all_entities.extend(entities)

    human_names = set()
    countries = set()
    dates = set()
    places = set()
    cities = set()

    for entity in all_entities:
        label = entity["label"]
        text = entity["text"].strip()
        text_lower = text.lower()

        # Add to appropriate category, filtering out pronouns from human names
        if label == "Person" and text_lower not in pronoun_list:
            human_names.add(text)
        elif label == "Country":
            country = is_it_a_nationality(filename, text) or text
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
        response.raise_for_status()

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

base_url = "https://encyclopedia.mathaf.org.qa/"
visited_urls = set()  
urls_to_visit = [base_url]  
bio_urls = []

# Crawl the website and collect bio URLs
while urls_to_visit:
    current_url = urls_to_visit.pop(0)

    if current_url in visited_urls:
        continue

    print(f"Crawling: {current_url}")

    new_links = crawl_page(current_url)
    visited_urls.add(current_url)
    urls_to_visit.extend(new_links)

    # If the URL contains '/bios/Pages', add it to the bio_urls list
    if '/bios/Pages' in current_url:
        if 'init=' in current_url or 'default' in current_url:
            continue  # Skip URLs containing 'init='
        bio_urls.append(current_url)

print(f"Crawling finished. Found {len(bio_urls)} bio pages.")

# scrape each bio page, extract entities, and generate word clouds
for bio_url in bio_urls:
    print(f"Scraping bio page: {bio_url}")
    response = requests.get(bio_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the Biography and Exhibitions headers
    biography_h1 = soup.find('h1', string=lambda text: text and 'biography' in text.lower())
    exhibitions_h1 = soup.find('h1', string=lambda text: text and 'exhibitions' in text.lower())

    biography_content = []

    if biography_h1 and exhibitions_h1:
        # Find the content between 'Biography' and 'Exhibitions'
        for sibling in biography_h1.find_next_siblings():
            if sibling == exhibitions_h1:
                break
            if sibling.name == 'p':  # Only collect <p> tags
                biography_content.append(sibling.get_text(strip=True))

    human_names, countries, dates, places, cities = extract_entities(biography_content)

    entity_counts = Counter()

    # Convert the lists to sets before using the union method
    all_entities_set = set(human_names).union(set(countries), set(dates), set(places), set(cities))

    for entity in all_entities_set:
        count = sum(chunk.count(entity) for chunk in biography_content)
        entity_counts[entity] = count

    # Sort entities alphabetically
    sorted_entity_counts = sorted(entity_counts.items(), key=lambda x: x[0])

    # Create a file path for the CSV file in the "Mathaf Encyclopedia" folder
    csv_name = os.path.join(folder_name, bio_url.split('/')[-1].replace('.aspx', '') + '.csv')

    with open(csv_name, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        # Write the header row
        writer.writerow(['Link', 'Entity', 'Occurrences'])
        # Write the link in the first row and leave it blank for subsequent rows
        link_written = False
        for entity, count in sorted_entity_counts:
            if not link_written:
                writer.writerow([bio_url, entity, count])
                link_written = True
            else:
                writer.writerow(['', entity, count])

    print(f"Entities and their occurrences have been saved to {csv_name}")

    word_cloud_image = generate_word_cloud(csv_name, os.path.join(folder_name, bio_url.split('/')[-1].replace('.aspx', '') + '_wordcloud.png'))
 
    if word_cloud_image:
        print(f"Word cloud has been saved.")
    else:
        print(f"Failed to generate word cloud for {bio_url}. The result is None.")

end_time = time.time()
execution_time = end_time - start_time
print(f"\nExecution time: {execution_time} seconds")
