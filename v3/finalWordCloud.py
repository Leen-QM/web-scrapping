import csv
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

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
                    frequency = int(row[3])  # The frequency count
                    word_freq[entity] = frequency
                except ValueError:
                    print(f"Skipping invalid frequency value in row: {row}")
                    continue

        if not word_freq:
            print(f"No valid data found in the file '{csv_file}'. No word cloud will be created.")
            return None

        # Dynamically get the font path relative to the script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(script_dir, "DejaVuSans.ttf")

        print("Generating the word cloud...")
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white',
            font_path=font_path  # Specify the embedded font
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
