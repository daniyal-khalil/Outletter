import requests
from bs4 import BeautifulSoup
import random
from google.cloud import vision
import io
import os
import webcolors

allowedTags = ["T-shirt", "Sweatshirt", "Jeans", "Sweater", "Jacket", "Coat", "Pants", "Trousers", "Shorts", "Shirt", "Blazer", "Vest", "Hoodie", "Skirt", "Blouse", "Sundress"]
colors = ["Blue", "Black", "Red", "White", "Grey", "Brown", "Yellow", "Orange", "Azure", "Purple", "Pink", "Green", "Violet"]


class TaggingEngine():
	def __init__(self, file):
		os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/code/resources/keyFile.json'
		self.file = file
		self.content = None
		with io.open(self.file, 'rb') as image_file:
			self.content = image_file.read()

	def tagImage( self, url, gender, debug=False):
		tags = self.detect_labels()
		filtered = [a for a in tags if a in allowedTags or a in colors]
		texts = self.detect_text()
		results = self.scrapeResults( "site:" + url + " " + ' '.join(filtered) + ' '.join( texts))
		if debug:
			print(results)
			print('=============')
			print(texts)
			print('=============')
			print(filtered)
			return {
				"links": results,
				"texts": texts,
				"tags": filtered
			}
		else:
			return {
				"links": results
			}


	def detect_labels(self):
		client = vision.ImageAnnotatorClient()

		image = vision.Image(content=self.content)

		response = client.label_detection(image=image)
		labels = response.label_annotations

		tags = []
		for label in labels:
			tags.append(label.description)

		if response.error.message:
			raise Exception(
				'{}\nFor more info on error messages, check: '
				'https://cloud.google.com/apis/design/errors'.format(
					response.error.message))
		return tags

	def detect_text(self):
		client = vision.ImageAnnotatorClient()

		image = vision.Image(content=self.content)

		response = client.text_detection(image=image)
		texts = response.text_annotations

		texts = []
		for text in texts:
			texts.append( text.description.replace("\n", ""))

		if response.error.message:
			raise Exception(
				'{}\nFor more info on error messages, check: '
				'https://cloud.google.com/apis/design/errors'.format(
					response.error.message))
		return texts

	def scrapeResults(self, query):
		query = query.replace(":", "%3A").replace(
			" ", "+").replace("/", "%2F").replace("@", "%40")
		text = '' + query
		url = 'https://www.google.com/search?q=' + text + '&source=lnms&tbm=isch'
		A = ("Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
				"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
				"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
				)

		Agent = A[random.randrange(len(A))]

		headers = {'user-agent': Agent}
		r = requests.get(url, headers=headers)

		links = []
		soup = BeautifulSoup(r.text, 'lxml')
		count = 0
		for info in soup.findAll('a', href=True):
			if(count < 10 and info['href'].startswith('https://www.koton.com')):
				links.append( info['href'])
				count += 1

		return links
