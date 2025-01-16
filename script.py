import spacy
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

table = soup.findAll('div')
for x in table:
    p_tags = x.findAll('p')  
    for p_tag in p_tags:
        p_text = p_tag.get_text().strip()  # Extract and clean the text
        
        # If the text is not already in the set, add it to both the set and the text variable
        if p_text and p_text not in seen_text:
            seen_text.add(p_text)
            text += p_text + '\n\n'  

nlp=spacy.load("en_core_web_lg")
doc = nlp(text)


for token in doc.ents:
	#print(token.text, token.pos_)
	if token.label_ == 'GPE':
   		print(token.text, token.label_)

	elif token.label_ == 'PERSON':
		print(token.text, token.label_)

	elif token.label_ == 'DATE':
		print(token.text, token.label_)


end_time = time.time()
execution_time = end_time - start_time
print(f"Execution time: {execution_time} seconds")
#print(text)