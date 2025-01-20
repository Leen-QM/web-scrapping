import re  # Import regular expressions
from mapping import is_it_a_nationality
from gliner import GLiNER
import time
import requests
from bs4 import BeautifulSoup

filename = 'countries_and_demonyms.csv'
start_time = time.time()

# URL of the page to scrape
url = 'https://encyclopedia.mathaf.org.qa/en/bios/Pages/Ragheb-Ayad.aspx'
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

# Remove countries that are actual demonyms
valid_countries = set()

for country in countries:
    result = is_it_a_nationality(filename, country)
    if result:
        valid_countries.add(result)  
    else:
        valid_countries.add(country)  

# Sort entities for display
sorted_human_names = sorted(human_names)  # Alphabetical
sorted_valid_countries = sorted(valid_countries)  # Alphabetical
sorted_dates = sorted(dates, key=int)  # Numerical order (years only)
sorted_places = sorted(places)  # Alphabetical
sorted_cities = sorted(cities)  # Alphabetical

# Display categorized entities
print("\nHuman Names (Alphabetical):")
print(sorted_human_names)

print("\nValid Countries (Demonyms Identified):")
print(sorted_valid_countries)

print("\nDates (Years Only, Increasing Order):")
print(sorted_dates)

print("\nPlaces (Alphabetical):")
print(sorted_places)

print("\nCities (Alphabetical):")
print(sorted_cities)

# Execution time
end_time = time.time()
execution_time = end_time - start_time
print(f"\nExecution time: {execution_time} seconds")

# Print chunks
print("\nChunks:")
for i, chunk in enumerate(biography_content, start=1):
    print(f"Chunk {i}:\n{chunk}\n{'-' * 50}")
