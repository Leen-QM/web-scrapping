import requests
from gliner import GLiNER
from finalMapping import is_it_a_nationality
from finalWordCloud import generate_word_cloud
import re
import csv
import os

# Initialize GLiNER with the base model
model = GLiNER.from_pretrained("urchade/gliner_small-v2.1")

# Predefined list of common pronouns (case-insensitive)
pronoun_list = {"he", "she", "him", "her", "it", "they", "them", "we", "us", "i", "me", "you", "his", "their", "our"}

# Define labels for entity prediction
labels = ["Human", "Country", "Date", "Era", "Person"]

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

# Function to extract entities and display all related labels with thresholds
def extract_entities_with_thresholds(biography_content):
    """
    Extract entities from the content and display all related labels with confidence thresholds.
    """
    entity_to_labels_with_thresholds = {}  # Dictionary to map entities to their labels and thresholds

    for chunk in biography_content:
        entities = model.predict_entities(chunk, labels, threshold=0.0)  # Set threshold to 0 to get all predictions

        for entity in entities:
            label = entity["label"]
            text = entity["text"].strip()
            score = entity["score"]  # Confidence score for the prediction

            # Add or update the entity in the dictionary
            if text in entity_to_labels_with_thresholds:
                entity_to_labels_with_thresholds[text].append((label, score))
            else:
                entity_to_labels_with_thresholds[text] = [(label, score)]

    # Print extracted entities with related labels and thresholds
    print("\nExtracted Entities with All Related Labels and Confidence Thresholds:")
    for entity, label_thresholds in entity_to_labels_with_thresholds.items():
        label_thresholds_str = ", ".join([f"{label} ({threshold:.2f})" for label, threshold in label_thresholds])
        print(f"{entity}: {label_thresholds_str}")

    return entity_to_labels_with_thresholds

# Function to process content and save results
def process_bio_page(bio_url, biography_content, folder_name="Mathaf Encyclopedia"):
    os.makedirs(folder_name, exist_ok=True)

    # Extract entities with labels and thresholds
    entities_with_labels_and_thresholds = extract_entities_with_thresholds(biography_content)

    # Save results to CSV
    csv_name = os.path.join(folder_name, bio_url.split('/')[-1].replace('.aspx', '') + '.csv')
    with open(csv_name, mode='w', newline='', encoding='utf-8-sig') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Entity', 'Related Labels and Thresholds'])  # Header row
        for entity, label_thresholds in entities_with_labels_and_thresholds.items():
            label_thresholds_str = ", ".join([f"{label} ({threshold:.2f})" for label, threshold in label_thresholds])
            writer.writerow([entity, label_thresholds_str])

    print(f"Entities saved to {csv_name}")

    # Generate word cloud
    word_cloud_image = generate_word_cloud(csv_name, bio_url, os.path.join(folder_name, bio_url.split('/')[-1].replace('.aspx', '') + '_wordcloud.png'))
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
