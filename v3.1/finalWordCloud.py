import csv
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def generate_word_cloud(csv_file,title, save_path=None):
    """
    Generate a word cloud from a CSV file of entities and their frequencies, and save it to a file.

    Args:
        csv_file (str): The path to the CSV file containing link, entities, and their counts.
        save_path (str, optional): The path to save the word cloud image. If None, the word cloud will not be saved.
        title (str, optional): The title to add to the word cloud image. Default is "Word Cloud of Entities".

    Returns:
        None: The function saves the word cloud to the specified file path if provided.
    """
    try:
        # Read the CSV file and create a dictionary of words and their frequencies
        word_freq = {}
        with open(csv_file, mode='r', encoding='iso-8859-2') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            for row in reader:
                # Ensure row has at least 3 columns (Link, Entity, Occurrences)
                if len(row) < 4:
                    print(f"Skipping invalid row: {row}")
                    continue
                try:
                    entity = row[1].strip()  # The entity name is in the second column
                    frequency = int(row[3])  # The frequency count is in the third column
                    word_freq[entity] = frequency
                except ValueError:
                    print(f"Skipping invalid frequency value in row: {row}")
                    continue

        # Check if word_freq is empty
        if not word_freq:
            print(f"No valid data found in the file '{csv_file}'. No word cloud will be created.")
            return None

        # Generate the word cloud
        wordcloud = WordCloud(width=900, height=400, background_color='white').generate_from_frequencies(word_freq)

        # If saving the word cloud as a PNG file
        if save_path: 
            # Create the figure for displaying
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')  # Turn off axes
            plt.title(title, fontsize=10, loc='left',pad = 15)  # Set the title of the plot

            # Save the word cloud image to the specified path
            plt.savefig(save_path, format='png')
            plt.close()  # Close the plot to avoid displaying it after saving
            print(f"Word cloud saved to {save_path}.")
            return wordcloud
        else:
            # Display the word cloud with a title
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')  # Turn off axes
            plt.title(title, fontsize=10, loc='left', pad = 15)  # Set the title
            plt.show()
            return wordcloud

    except FileNotFoundError:
        print(f"Error: The file '{csv_file}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
