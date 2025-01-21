import re  # Import regular expressions
import csv  # For writing to CSV
from mapping import is_it_a_nationality
from wordCloud import generate_word_cloud  # Import the word cloud function
from gliner import GLiNER
import time
import requests
from bs4 import BeautifulSoup
from collections import Counter

filename = 'countries_and_demonyms.csv'
start_time = time.time()

# URL of the page to scrape
url = 'https://encyclopedia.mathaf.org.qa/en/bios/Pages/Ragheb-Ayad.aspx'
response = requests.get(url)

# Parse the webpage content
soup = BeautifulSoup(response.text, 'html.parser')

# Extract the name for the CSV filename from the URL
csv_name = url.split('/')[-1].replace('.aspx', '') + '.csv'

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

# Sort entities alphabetically
sorted_entity_counts = sorted(entity_counts.items(), key=lambda x: x[0])

# Write the results to a CSV file with the link in the first row only
with open(csv_name, mode='w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    # Write the header row
    writer.writerow(['Link', 'Entity', 'Occurrences'])
    # Write the link in the first row and leave it blank for subsequent rows
    link_written = False
    for entity, count in sorted_entity_counts:
        if not link_written:
            writer.writerow([url, entity, count])
            link_written = True
        else:
            writer.writerow(['', entity, count])

# Print a success message
print(f"\nEntities and their occurrences have been saved to {csv_name}")

# Call the generate_word_cloud function to display the word cloud
generate_word_cloud(csv_name)

# Execution time
end_time = time.time()
execution_time = end_time - start_time
print(f"\nExecution time: {execution_time} seconds")
