import time
import os
import requests
from boilerpy3 import extractors
from scraper import scrape_bio_page  # Import the scrape function
from finalCrawling import crawl_page  # Existing crawling function

# Function to split content into word-safe chunks
def split_into_chunks(content, chunk_size=500):
    """
    Splits the content into smaller chunks without cutting words.

    :param content: The text content to split
    :param chunk_size: Maximum size of each chunk
    :return: A list of smaller chunks
    """
    words = content.split()  # Split content into words
    chunks = []
    current_chunk = []

    for word in words:
        # Check if adding the next word exceeds the chunk size
        if len(" ".join(current_chunk + [word])) > chunk_size:
            # Save the current chunk and start a new one
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
        else:
            current_chunk.append(word)

    # Add the last chunk if it contains any words
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

# Function to fetch main content between user-defined phrases
def fetch_main_content_advanced(url, start_phrase, end_phrase):
    # Use the default extractor, which is optimized for general-purpose content extraction
    extractor = extractors.DefaultExtractor()
    
    # Fetch the main content from the URL
    response = requests.get(url)
    if response.status_code == 200:
        # Extract the main content
        content = extractor.get_content(response.text)
        
        # Find content between the specified phrases
        start_index = content.find(start_phrase)
        end_index = content.find(end_phrase, start_index)

        # Check if both phrases are found
        if start_index != -1 and end_index != -1:
            extracted_content = content[start_index:end_index].strip()
            return split_into_chunks(extracted_content)  # Split into word-safe chunks
        else:
            return ["Specified phrases not found in the content."]
    else:
        raise Exception(f"Failed to fetch {url}, status code: {response.status_code}")


# Main program starts here
start_time = time.time()

# Create a folder called "Mathaf Encyclopedia" if it doesn't already exist
folder_name = "Mathaf Encyclopedia"
os.makedirs(folder_name, exist_ok=True)

# Ask the user for inputs
base_url = input("Enter the base URL to start crawling: ").strip()
specified_path = input("Enter the specified path to filter (e.g., 'bios'): ").strip()
start_phrase = input("Enter the starting phrase for content extraction: ").strip()
end_phrase = input("Enter the ending phrase for content extraction: ").strip()

visited_urls = set()  # Set to store visited URLs
urls_to_visit = [base_url]  # List to store URLs to visit next
bio_urls = []  # List to store URLs with the specified path

# Crawl the website and collect bio URLs
while urls_to_visit:
    current_url = urls_to_visit.pop(0)  # Dequeue the first URL

    if current_url in visited_urls:
        continue

    print(f"Crawling: {current_url}")

    new_links = crawl_page(current_url)
    visited_urls.add(current_url)
    urls_to_visit.extend(new_links)

    # If the URL contains the specified path, add it to the bio_urls list
    if specified_path in current_url:
        if 'init=' in current_url or 'default' in current_url:
            continue  # Skip URLs containing 'init='
        bio_urls.append(current_url)

print(f"Crawling finished. Found {len(bio_urls)} pages containing '{specified_path}'.")

# Process each bio page to extract content based on user-defined phrases
for bio_url in bio_urls:
    print(f"\nProcessing: {bio_url}")
    try:
        # Fetch content between the user-defined phrases
        content_chunks = fetch_main_content_advanced(bio_url, start_phrase, end_phrase)
        print(f"Extracted Chunks from {bio_url}:\n")
        for chunk in content_chunks:
            print(chunk)

        # Pass the extracted chunks directly to the scrape_bio_page function
        scrape_bio_page(bio_url, content_chunks, folder_name)

    except Exception as e:
        print(f"Error processing {bio_url}: {e}")

# Execution time
end_time = time.time()
execution_time = end_time - start_time
print(f"\nExecution time: {execution_time} seconds")
import time
import os
import requests
from boilerpy3 import extractors
from scraper import scrape_bio_page  # Import the scrape function
from finalCrawling import crawl_page  # Existing crawling function

# Function to split content into word-safe chunks
def split_into_chunks(content, chunk_size=500):
    """
    Splits the content into smaller chunks without cutting words.

    :param content: The text content to split
    :param chunk_size: Maximum size of each chunk
    :return: A list of smaller chunks
    """
    words = content.split()  # Split content into words
    chunks = []
    current_chunk = []

    for word in words:
        # Check if adding the next word exceeds the chunk size
        if len(" ".join(current_chunk + [word])) > chunk_size:
            # Save the current chunk and start a new one
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
        else:
            current_chunk.append(word)

    # Add the last chunk if it contains any words
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

# Function to fetch main content between user-defined phrases
def fetch_main_content_advanced(url, start_phrase, end_phrase):
    # Use the default extractor, which is optimized for general-purpose content extraction
    extractor = extractors.DefaultExtractor()
    
    # Fetch the main content from the URL
    response = requests.get(url)
    if response.status_code == 200:
        # Extract the main content
        content = extractor.get_content(response.text)
        
        # Find content between the specified phrases
        start_index = content.find(start_phrase)
        end_index = content.find(end_phrase, start_index)

        # Check if both phrases are found
        if start_index != -1 and end_index != -1:
            extracted_content = content[start_index:end_index].strip()
            return split_into_chunks(extracted_content)  # Split into word-safe chunks
        else:
            return ["Specified phrases not found in the content."]
    else:
        raise Exception(f"Failed to fetch {url}, status code: {response.status_code}")


# Main program starts here
start_time = time.time()

# Create a folder called "Mathaf Encyclopedia" if it doesn't already exist
folder_name = "Mathaf Encyclopedia"
os.makedirs(folder_name, exist_ok=True)

# Ask the user for inputs
base_url = input("Enter the base URL to start crawling: ").strip()
specified_path = input("Enter the specified path to filter (e.g., 'bios'): ").strip()
start_phrase = input("Enter the starting phrase for content extraction: ").strip()
end_phrase = input("Enter the ending phrase for content extraction: ").strip()

visited_urls = set()  # Set to store visited URLs
urls_to_visit = [base_url]  # List to store URLs to visit next
bio_urls = []  # List to store URLs with the specified path

# Crawl the website and collect bio URLs
while urls_to_visit:
    current_url = urls_to_visit.pop(0)  # Dequeue the first URL

    if current_url in visited_urls:
        continue

    print(f"Crawling: {current_url}")

    new_links = crawl_page(current_url)
    visited_urls.add(current_url)
    urls_to_visit.extend(new_links)

    # If the URL contains the specified path, add it to the bio_urls list
    if specified_path in current_url:
        if 'init=' in current_url or 'default' in current_url:
            continue  # Skip URLs containing 'init='
        bio_urls.append(current_url)

print(f"Crawling finished. Found {len(bio_urls)} pages containing '{specified_path}'.")

# Process each bio page to extract content based on user-defined phrases
for bio_url in bio_urls:
    print(f"\nProcessing: {bio_url}")
    try:
        # Fetch content between the user-defined phrases
        content_chunks = fetch_main_content_advanced(bio_url, start_phrase, end_phrase)
        print(f"Extracted Chunks from {bio_url}:\n")
        for chunk in content_chunks:
            print(chunk)

        # Pass the extracted chunks directly to the scrape_bio_page function
        scrape_bio_page(bio_url, content_chunks, folder_name)

    except Exception as e:
        print(f"Error processing {bio_url}: {e}")

# Execution time
end_time = time.time()
execution_time = end_time - start_time
print(f"\nExecution time: {execution_time} seconds")
