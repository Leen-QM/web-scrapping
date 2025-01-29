import csv
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import arabic_reshaper
from bidi.algorithm import get_display
import unicodedata

def is_arabic_text(text):
    """
    Check if the given text contains Arabic characters.

    Args:
        text (str): The text to check.

    Returns:
        bool: True if the text contains Arabic characters, False otherwise.
    """
    for char in text:
        if "ARABIC" in unicodedata.name(char, ""):
            return True
    return False

def generate_word_cloud(csv_file, title, save_path=None):
    try:
        # Read the CSV file and create a dictionary of words and their frequencies
        word_freq = {}
        with open(csv_file, mode='r', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            for row in reader:
                if len(row) < 4:  # Validate row length
                    print(f"Skipping invalid row: {row}")
                    continue
                try:
                    entity = row[1].strip()  # The entity name
                    if is_arabic_text(entity):  # Check if the text is Arabic
                        reshaped_entity = arabic_reshaper.reshape(entity)  # Reshape for proper display
                        bidi_entity = get_display(reshaped_entity)  # Adjust for RTL
                    else:
                        bidi_entity = entity  # Use the original text for non-Arabic entities
                    frequency = int(row[3])  # The frequency count
                    word_freq[bidi_entity] = frequency
                except ValueError:
                    print(f"Skipping invalid frequency value in row: {row}")
                    continue

        if not word_freq:
            print(f"No valid data found in the file '{csv_file}'. No word cloud will be created.")
            return None

        # Dynamically select the font path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        arabic_font_path = os.path.join(script_dir, "Amiri-Regular.ttf")
        english_font_path = os.path.join(script_dir, "DejaVuSans.ttf")
        selected_font = arabic_font_path if any(is_arabic_text(key) for key in word_freq.keys()) else english_font_path

        print(f"Using font: {selected_font}")
        print("Generating the word cloud...")
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white',
            font_path=selected_font  # Specify the selected font
        ).generate_from_frequencies(word_freq)
        print("Word cloud generated successfully.")

        if save_path:
            print(f"Saving the word cloud to {save_path}...")
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title(title, fontsize=16)
            plt.savefig(save_path, format='png')
            plt.close()
            print(f"Word cloud saved to {save_path}.")
        else:
            print("Displaying the word cloud...")
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title(title, fontsize=16)
            plt.show()

    except FileNotFoundError:
        print(f"Error: The file '{csv_file}' was not found.")
    except PermissionError:
        print(f"Permission error: Unable to save the word cloud to '{save_path}'. Please check file permissions.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# Example usage
if __name__ == "__main__":
    csv_file = input("Enter the path to the CSV file: ").strip()
    title = input("Enter the title for the word cloud: ").strip()
    save_path = input("Enter the path to save the word cloud image (or press Enter to display only): ").strip() or None

    generate_word_cloud(csv_file, title, save_path)
