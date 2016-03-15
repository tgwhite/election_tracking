#### parse election results reported by Politico, by county ####

from bs4 import BeautifulSoup
import requests, io, os
import pandas as pd
import numpy as np
import re 
from datetime import date 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

# using info on states that have held primaries, get county level data

main_url = "http://www.politico.com/2016-election/results/map/president"

### some elements parsed here are not fully loaded when requests.get() is run. Alternative is to 
# run the get with selenium
# available_states = requests.get(main_url)
# available_states_soup = BeautifulSoup(available_states.content)

driver = webdriver.Firefox()
driver.get(main_url)
available_states = driver.page_source
available_states_soup = BeautifulSoup(available_states)
driver.close()

articles = available_states_soup.findAll('article', {'class': 'results-group'})

detailed_results_links = []
for article in articles: 
	article_links = article.findAll('a')
	detailed_results_link = [x.get('href') for x in article_links if '2016-election/results/map/president/' in x.get('href')][0]	
	detailed_results_links.append(detailed_results_link)

# get unique set of detailed results links
detailed_results_links = list(set(detailed_results_links))

# go through each state's results and get county by county info, if available

driver = webdriver.Firefox()

all_county_dat = []
for state_detailed in detailed_results_links: 
	
	state = state_detailed.split('/')[-2]
	print('working on', state, "...\n")
	driver.get(state_detailed)			

	# state_soup = BeautifulSoup(requests.get(state_detailed).content)
	state_soup = BeautifulSoup(driver.page_source)	

	loading_h4 = state_soup.findAll('h4', {'class': 'is-loading'})
	it = 0
	while len(loading_h4) > 0 and it < 100: 
		print('waiting...')
		it += 1		
		time.sleep(1)		
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # scroll to the bottom of the page to enforce loading
		state_soup = BeautifulSoup(driver.page_source)
		loading_h4 = state_soup.findAll('h4', {'class': 'is-loading'})

	page_h2 = state_soup.findAll('h2')
	has_county_results = len([x.get_text().lower() for x in page_h2 if 'results by county' in x.get_text().lower()]) > 0

	if not has_county_results:		
		print('no county results for', state, '\n') 
		results_articles = [x for x in state_soup.findAll('article', {'class': 'results-group'}) if x.get('data-fips') is not None]
		summary_level = 'state'
	else: 
		results_articles = [x for x in state_soup.findAll('article', {'class': 'results-group'}) if x.get('data-fips') is not None and x.get('data-fips') != '0']
		summary_level = 'county'

	if len(results_articles) == 0: 
		print('no results articles for', state, 'continuing')
		continue
	
	for result in results_articles: 		
		try: 
			if summary_level == 'state': 
				title = result.find('h2').get_text()
			else: 
				title = result.find('h4').get_text()
		except Exception as e: 
			print(state)
			print('exception with title\n')
			print(e)
			continue
		
		results_tables = result.findAll('table', {'class': 'results-table'})
		
		for result_table in results_tables: 			
			table_type = result_table.find('tr').get('class')[0].replace('type-', '').upper()
			table_rows = result_table.findAll('tr')
			
			for row in table_rows: 				
				candidate = row.find('th').get_text()
				percentage = row.find('span', {'class': 'percentage-combo'}).get_text()
				popular_vote = row.find('td', {'class': 'results-popular'}).get_text()

				out_dict = {
					'candidate': candidate, 
					'percentage': percentage,
					'popular_vote': popular_vote, 
					'county': title, 
					'state' : state,
					'party': table_type,
					'summary_level': summary_level
				}
				all_county_dat.append(out_dict)

# pack everything up and export
all_county_dat_df = pd.DataFrame(all_county_dat)
all_county_dat_df.to_csv('all_primary_results_by_county.csv', index = False)

driver.close()
driver.quit()