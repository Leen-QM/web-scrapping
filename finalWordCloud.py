import csv
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def generate_word_cloud(csv_file):
    """
    Generate and display a word cloud from a CSV file of entities and their frequencies.
    
    Args:
        csv_file (str): The path to the CSV file containing link, entities, and their counts.
    """
    try:
        # Read the CSV file and create a dictionary of words and their frequencies
        word_freq = {}
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            for row in reader:
                # Ensure row has at least 3 columns (Link, Entity, Occurrences)
                if len(row) < 3:
                    print(f"Skipping invalid row: {row}")
                    continue
                try:
                    entity = row[1].strip()  # The entity name is in the second column
                    frequency = int(row[2])  # The frequency count is in the third column
                    word_freq[entity] = frequency
                except ValueError:
                    print(f"Skipping invalid frequency value in row: {row}")
                    continue

        # Check if word_freq is empty
        if not word_freq:
            print(f"No valid data found in the file '{csv_file}'. No word cloud will be created.")
            return

        # Generate the word cloud
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_freq)

        # Display the word cloud
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')  # Turn off axes
        plt.title("Word Cloud of Entities", fontsize=16)
        plt.show()

    except FileNotFoundError:
        print(f"Error: The file '{csv_file}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
