import re  # Import regular expressions
from mapping import is_it_a_nationality
from gliner import GLiNER
import time
import requests
from bs4 import BeautifulSoup
from collections import Counter

filename = 'countries_and_demonyms.csv'
start_time = time.time()

# URL of the page to scrape
url = 'https://www.encyclopedia.mathaf.org.qa/en/bios/Pages/Cesar-Gemayel.aspx'
response = requests.get(url)

# Parse the webpage content
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

# Initialize GLiNER with the base model
model = GLiNER.from_pretrained("urchade/gliner_multi-v2.1")

# Define labels for entity prediction
labels = ["Person", "Country", "Date", "Place", "City"]

all_entities = []

# Extract entities from each chunk
for chunk in biography_content:
    entities = model.predict_entities(chunk, labels, threshold=0.5)
    all_entities.extend(entities)

# Predefined list of common pronouns (case-insensitive)
pronoun_list = {"he", "she", "him", "her", "it", "they", "them", "we", "us", "i", "me", "you", "his", "their", "our"}

# Initialize final sets
human_names = set()
countries = set()
dates = set()
places = set()
cities = set()

# Categorize entities into separate sets
for entity in all_entities:
    label = entity["label"]
    text = entity["text"].strip()

    if label == "Person" and text.lower() not in pronoun_list:
        human_names.add(text)
    elif label == "Country":
        country = is_it_a_nationality(filename, text) or text
        countries.add(country)
    elif label == "Date":
        match = re.search(r'\b\d{4}\b', text)
        if match:
            dates.add(match.group(0))
    elif label == "Place":
        places.add(text)
    elif label == "City":
        cities.add(text)

# Count occurrences of each entity in the final sets
entity_counts = Counter()

# Combine all entities into a single set
all_entities_set = human_names.union(countries, dates, places, cities)

for entity in all_entities_set:
    count = sum(chunk.count(entity) for chunk in biography_content)
    entity_counts[entity] = count

# Print the results as a table
print(f"{'Entity':<30}{'Occurrences':<15}")
print("-" * 45)
for entity, count in entity_counts.items():
    print(f"{entity:<30}{count:<15}")

# Execution time
end_time = time.time()
execution_time = end_time - start_time
print(f"\nExecution time: {execution_time} seconds")

sorted_human_names = sorted(human_names)  # Alphabetical
sorted_countries = sorted(countries)  # Alphabetical
sorted_dates = sorted(dates, key=int)  # Numerical order (years only)
sorted_places = sorted(places)  # Alphabetical
sorted_cities = sorted(cities)  # Alphabetical

# Display categorized entities
print("\nHuman Names (Alphabetical):")
print(sorted_human_names)

print("\nCountries (Alphabetical, Demonyms Removed):")
print(sorted_countries)

print("\nDates (Years Only, Increasing Order):")
print(sorted_dates)

print("\nPlaces (Alphabetical):")
print(sorted_places)

print("\nCities (Alphabetical):")
print(sorted_cities)
