
### Downloads and outputs state of the union speeches from UCSB

from bs4 import BeautifulSoup
import requests, io, os
import pandas as pd
import numpy as np
import json

state_of_union_base = 'http://www.presidency.ucsb.edu/sou.php'

sou_soup = BeautifulSoup(requests.get(state_of_union_base).content)

speech_links = [x.find('a') for x in sou_soup.findAll('td', {"class": "ver12"}) if x.find('a') is not None]
speech_links = [x for x in speech_links if x.get_text() is not None]

all_speech_contents = []

for speech_link in speech_links: 
	the_speech_link = speech_link['href']

	try: 
		speech_soup = BeautifulSoup(requests.get(the_speech_link).content)

		president_name = [x.get('alt') for x in speech_soup.findAll('img') if 'images/names' in x.get('src') ][0]
		speech_date = speech_soup.find('span', {'class': 'docdate'}).get_text()
		all_speech_paragraphs = [x.get_text() for x in speech_soup.findAll('p')]
		
		print(speech_date)

		out_dict = {
			"president_name": president_name,
			"speech_date": speech_date,
			"speech": all_speech_paragraphs
		}

		all_speech_contents.append(out_dict)
	except Exception as e: 
		print(e)


with open('state_of_the_union_text.json', 'w') as outfile:
	json.dump(all_speech_contents, outfile)