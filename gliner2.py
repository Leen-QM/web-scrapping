from gliner import GLiNER
import time
import requests
from bs4 import BeautifulSoup

start_time = time.time()

url = 'https://encyclopedia.mathaf.org.qa/en/bios/Pages/Ragheb-Ayad.aspx'
response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')
page_text  = soup.get_text()
text = ""
seen_text = set()
all_entities = []

table = soup.findAll('div')
for x in table:
    p_tags = x.findAll('p')  
    for p_tag in p_tags:
        p_text = p_tag.get_text().strip()  # Extract and clean the text
        
        # If the text is not already in the set, add it to both the set and the text variable
        if p_text and p_text not in seen_text:
            seen_text.add(p_text)
            text += p_text + '\n\n'  


# Initialize GLiNER with the base model
model = GLiNER.from_pretrained("urchade/gliner_medium-v2.1")

def chunk_text(text, max_length=384):
	return [text[i:i+max_length] for i in range(0, len(text), max_length)]

if len(text) > 384:
	chunks = chunk_text(text)
	print("Number of chunks:", len(chunks))
else:
	chunks = [text]

# Labels for entity prediction
# Most GLiNER models should work best when entity types are in lower case or title case
labels = ["Person", "Country", "Date", "Location", "City" ]

for chunk in chunks:
	entities = model.predict_entities(chunk, labels, threshold=0.5)
	all_entities.extend(entities)

# Perform entity prediction
#entities = model.predict_entities(text, labels, threshold=0.5)

# Display predicted entities and their labels
for entity in all_entities:
    print(entity["text"], "=>", entity["label"])

end_time = time.time()
execution_time = end_time - start_time
print(f"Execution time: {execution_time} seconds")
