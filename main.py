import re
import os
import sys
import csv
import json
import time
import requests
import schedule
import tkinter as tk

from tkinter import simpledialog, messagebox, filedialog
from datetime import datetime


CARD_ID = ''
def write_card_data():
	if CARD_ID == '':
		raise Exception('No Card ID passed.')

	response = requests.get(f'https://api.pikastocks.com/card_sets/{CARD_ID}')
	data = json.loads(response.text)
	file_name = filedialog.asksaveasfilename()
	file_exists = os.path.exists(file_name)
	with open(file_name, mode='a+') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=[
			'name',
			'rarity',
			'collector_number',
			'scrape_date',
			'foil',
			'market',
			'market_foil',
			'average',
			'ath',
			'atl',
		])
		# only write header for new file
		if not file_exists:
			writer.writeheader()

		for card_object in data['prints']:
			writer.writerow({
				'name': card_object['name'],
				'rarity': card_object['rarity'],
				'collector_number': card_object['collector_number'],
				'scrape_date': datetime.today().strftime("%d/%m/%y"),
				'foil': card_object['latest_price']['foil'],
				'market': card_object['latest_price']['market'],
				'market_foil': card_object['latest_price']['market_foil'],
				'average': card_object['latest_price']['avg'],
				'ath': '',
				'atl': ''
			})
	messagebox.showinfo(title='Completed Process.', message=f'{file_name} has been recently updated.')

regex = re.compile(
	r'^(?:http|ftp)s?://' # http:// or https://
	r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
	r'localhost|' #localhost...
	r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
	r'(?::\d+)?' # optional port
	r'(?:/?|[/?]\S+)$', re.IGNORECASE)

ROOT = tk.Tk()
ROOT.withdraw()
url = simpledialog.askstring(title='PikaStock Scraper', prompt="Enter URL")

is_valid_url = re.match(regex, url)
if is_valid_url:
	parts = url.split('/')
	path = parts.pop()
	CARD_ID = path.split('-')[0]
	try: 
		schedule.every().day.do(write_card_data)
		while True:
			schedule.run_pending()
			time.sleep(1)
	except KeyboardInterrupt:
		sys.exit(0)
else:
	messagebox.showerror(title='Invalid URL', message='This is an invalid URL.')

