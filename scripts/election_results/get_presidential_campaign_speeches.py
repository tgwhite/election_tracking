
### Downloads and outputs state of the union speeches from UCSB

from bs4 import BeautifulSoup
import requests, io, os
import pandas as pd
import numpy as np
import json

base_url = 'http://www.presidency.ucsb.edu/'

campaign_speech_mains = [
	"http://www.presidency.ucsb.edu/2008_election.php",
	"http://www.presidency.ucsb.edu/2012_election.php",
	"http://www.presidency.ucsb.edu/2016_election.php"
]

all_speech_contents = []

for speech_main in campaign_speech_mains: 

	speech_main_soup = BeautifulSoup(requests.get(speech_main).content)

	candidate_speech_page_links = [x for x in speech_main_soup.findAll('a') if 'campaign speeches' in x.get_text()]

	for candidate_speech_page in candidate_speech_page_links: 
		
		candidate_speech_page = candidate_speech_page['href']

		candidate_speech_page_soup = BeautifulSoup(requests.get(base_url + candidate_speech_page).content)

		indv_speech_pages = [x.find('a')['href'] for x in candidate_speech_page_soup.findAll('td', {"class": 'listdate'}) if x.find('a') is not None]

		for speech_page in indv_speech_pages: 
			try: 
				the_speech_page = speech_page.replace('../ws/', 'ws/')

				speech_soup = BeautifulSoup(requests.get(base_url + the_speech_page).content)
				candidate_name = [x.get('alt') for x in speech_soup.findAll('img') if 'images/names' in x.get('src') ][0]
				speech_title = speech_soup.find('span', {"class": 'paperstitle'}).get_text()
				speech_date = speech_soup.find('span', {'class': 'docdate'}).get_text()
				all_speech_paragraphs = [x.get_text() for x in speech_soup.findAll('p')]
				
				try: 
					print(candidate_name, speech_title, speech_date)
				except Exception as e: 
					print('error printing progress')
				
				out_dict = {
					"candidate_name": candidate_name,
					"speech_title": speech_title,
					"speech_date": speech_date,
					"speech": all_speech_paragraphs
				}
				all_speech_contents.append(out_dict)
				
			except Exception as e: 
				print('error!', e)
				print(speech_page)


	with open('presidential_campaign_speeches.json', 'w') as outfile:
		json.dump(all_speech_contents, outfile)