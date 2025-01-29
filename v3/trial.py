import requests
from gliner import GLiNER
from finalMapping import is_it_a_nationality
from finalMapping import is_arabic_country
from finalWordCloud import generate_word_cloud
import re
import csv
from collections import Counter
import os

# Initialize GLiNER with the base model
model = GLiNER.from_pretrained("urchade/gliner_multi-v2.1")

# Predefined list of common pronouns (case-insensitive)
pronoun_list = {"he", "she", "him", "her", "it", "they", "them", "we", "us", "i", "me", "you", "his", "their", "our"}

# Define labels for entity prediction
labels = ["Person", "Country", "Date", "Place", "City"]
labels2= ["اسم", "دولة", "تاريخ", "مكان", "مدينة"]

# Function to split content into word-safe chunks
def split_into_chunks(content, chunk_size=500):
    words = content.split()
    chunks = []
    current_chunk = []

    for word in words:
        if len(" ".join(current_chunk + [word])) > chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
        else:
            current_chunk.append(word)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

# Function to extract content between start and end phrases
def fetch_main_content_advanced(url, start_phrase, end_phrase):
    response = requests.get(url)
    if response.status_code == 200:
        content = response.text
        print(content)
        # Find content between the specified phrases
        start_index = content.find(start_phrase)
        end_index = content.find(end_phrase, start_index)

        if start_index != -1 and end_index != -1:
            extracted_content = content[start_index:end_index].strip()
            return split_into_chunks(extracted_content)  # Return chunks
        else:
            raise ValueError("Specified phrases not found in the content.")
    else:
        raise Exception(f"Failed to fetch {url}, status code: {response.status_code}")

def extract_entities(biography_content, bio_url):
    """
    Extract entities from the content based on the language specified in the URL.
    """
    all_entities = []
    print(bio_url)

    # Determine language and set appropriate labels
    if "/en/" in bio_url.lower():
        print("Language: English")
        language = "English"
        current_labels = labels
        threshold = 0.5
    elif "/ar/" in bio_url.lower():
        print("Language: Arabic")
        language = "Arabic"
        current_labels = labels2
        threshold = 0.6

    else:
        raise ValueError("Language not recognized. URL must contain '/en/' or '/ar/'.")

    for chunk in biography_content:
        entities = model.predict_entities(chunk, current_labels, threshold)
        all_entities.extend(entities)

    arabic_pattern = re.compile(r'[\u0600-\u06FF]')
    human_names = set()
    countries = set()
    dates = set()
    places = set()
    cities = set()

    for entity in all_entities:
        label = entity["label"]
        text = entity["text"].strip()
        if language == "English":
            # Process entities for English
            if label == "Person" and text[0].isupper() and text.lower() not in pronoun_list:
                human_names.add((text, label))
            elif label == "Country":
                country = is_it_a_nationality('countries_and_demonyms.csv', text) or text
                countries.add((country, label))
            elif label == "Date":
                match = re.search(r'\b(18|19|20)\d{2}\b', text)
                if match:
                    dates.add((match.group(0), label))
            elif label == "Place":
                places.add((text, label))
            elif label == "City":
                cities.add((text, label))

        elif language == "Arabic":
            if label in ["اسم", "دولة", "مكان", "مدينة"] and not arabic_pattern.search(text):
                continue
            # Process entities for Arabic
            if label == "اسم":
                human_names.add((text, label))
            elif label == "دولة":
                countries.add((text, label))
            elif label == "تاريخ":
                match = re.search(r'\b(18|19|20)\d{2}\b', text)
                if match:
                    dates.add((match.group(0), label))
            elif label == "مكان":
                places.add((text, label))
            elif label == "مدينة":
                if not is_arabic_country('countries_and_demonyms.csv', text):
                    cities.add((text, label))

    print(f"Processing chunk with labels: {current_labels} and threshold: {threshold}")
    sorted_human_names = sorted(human_names, key=lambda x: x[0])
    sorted_countries = sorted(countries, key=lambda x: x[0])
    sorted_dates = sorted(dates, key=lambda x: int(x[0]) if x[0].isdigit() else x[0])
    sorted_places = sorted(places, key=lambda x: x[0])
    sorted_cities = sorted(cities, key=lambda x: x[0])

    return sorted_human_names, sorted_countries, sorted_dates, sorted_places, sorted_cities


# Function to process content and save results
def process_bio_page(bio_url, biography_content, folder_name="Mathaf Encyclopedia"):
    os.makedirs(folder_name, exist_ok=True)
    human_names, countries, dates, places, cities = extract_entities(biography_content, bio_url)

    entity_label_counts = Counter()
    all_entities_set = set(human_names).union(set(countries), set(dates), set(places), set(cities))

    for entity_tuple in all_entities_set:
        entity = entity_tuple[0]
        count = sum(chunk.count(entity) for chunk in biography_content)
        label = entity_tuple[1]
        entity_label_counts[(entity, label)] = count

    sorted_entity_counts = sorted(entity_label_counts.items(), key=lambda x: x[0])

    csv_name = os.path.join(folder_name, bio_url.split('/')[-1].replace('.aspx', '') + '.csv')

    with open(csv_name, mode='w', newline='', encoding='utf-8-sig') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Link', 'Entity', 'Label', 'Occurrences'])
        for (entity, label), count in sorted_entity_counts:
            writer.writerow([bio_url, entity, label, count])

    print(f"Entities saved to {csv_name}")

    word_cloud_image = generate_word_cloud(csv_name, [bio_url], os.path.join(folder_name, bio_url.split('/')[-1].replace('.aspx', '') + '_wordcloud.png'))
    if word_cloud_image:
        print("Word cloud has been saved.")
    else:
        print("Failed to generate word cloud.")

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
