import requests
from bs4 import BeautifulSoup
import random
from google.cloud import vision
import io
import os
import webcolors
from scipy.spatial import KDTree

allowedTags = ["T-shirt", "Sweatshirt", "Jeans", "Sweater", "Jacket", "Coat", "Pants", "Trousers", "Shorts", "Shirt", "Blazer", "Vest", "Hoodie", "Skirt", "Blouse", "Sundress"]
colors = ["Blue", "Black", "Red", "White", "Grey", "Brown", "Yellow", "Orange", "Azure", "Purple", "Pink", "Green", "Violet"]
websites = ["www.koton.com", "www.lcwaikiki.com", "www.boyner.com.tr", "www.defacto.com.tr", "www.trendyol.com", "www2.hm.com/tr_tr"]


class TaggingEngine():
	def __init__(self, file):
		self.file = file
		self.content = None
		with io.open(self.file, 'rb') as image_file:
			self.content = image_file.read()

	def tagImage( self, url_index, gender, label, debug=False):
		tags = self.detect_labels()
		# color = ""
		# for x in tags:
		# 	if x in colors:
		# 		color = x
		# 		break
		
		filtered = [a for a in tags if a in allowedTags]
		texts = self.detect_text()
		dominant_colors = self.detect_color()
		# print(tags)
		# print(filtered)
		# print(texts)
		# print(color)
		results = self.scrapeResults( "site:" + websites[url_index] + " " + label + " " + gender + " " + ' '.join(dominant_colors) + " " + ' '.join(texts), 'https://' + websites[url_index])
		if debug:
			return {
				"links": results.get("links", []),
				"imageLinks": results.get("imageLinks", []),
				"texts": texts,
				"colors": dominant_colors,
				"tags": label
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
		
	
	def detect_color(self):
		client = vision.ImageAnnotatorClient()
		image = vision.Image(content=self.content)
		response = client.image_properties(image=image)
		props = response.image_properties_annotation
		hexnames = webcolors.CSS2_HEX_TO_NAMES
		
		running_sum = 0
		vision_colors = []
		for color in props.dominant_colors.colors:
			if running_sum > 80:
				break
			pixel_rounded = round(color.score*100)
			if(pixel_rounded > 10):
				# print((color.color.red,color.color.green,color.color.blue))
				vision_colors.append((color.color.red,color.color.green,color.color.blue))
		
		names = []
		positions = []
		rgbs = []
		
		for x in hexnames.items():
			names.append(x[1])
			rgbs.append(webcolors.hex_to_rgb(x[0]))
			positions.append(webcolors.hex_to_rgb(x[0]))
			
		spacedb = KDTree(positions)
		
		for x in rgbs:
			dist, index = spacedb.query(x)
			# print(names[index])
		
		dominant_colors = set({})
		for x in vision_colors:
			dist, index = spacedb.query(x)
			dominant_colors.add(names[index])
			
		return list(dominant_colors)
	
	
	def detect_text(self):
		client = vision.ImageAnnotatorClient()

		image = vision.Image(content=self.content)

		response = client.text_detection(image=image)
		texts = response.text_annotations
			
		vision_texts = set({})
		for text in texts:
			vision_texts.add(text.description.strip().replace("\n",""))

		if response.error.message:
			raise Exception(
				'{}\nFor more info on error messages, check: '
				'https://cloud.google.com/apis/design/errors'.format(
					response.error.message))
					
		vision_texts = [] if len(list(vision_texts)) > 2 else list(vision_texts)
		return vision_texts

	def scrapeResults(self, query, website):
		query = query.replace(":", "%3A").replace(
			" ", "+").replace("/", "%2F").replace("@", "%40")
		text = '' + query
		url = 'https://www.google.com/search?q=' + text + '&source=lnms&tbm=isch'
		A = ("Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
				"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
				"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
				)
		# print(url)
		Agent = A[random.randrange(len(A))]

		headers = {'user-agent': Agent}
		r = requests.get(url, headers=headers)
		MAX_RESULTS = 15

		links = []
		images = []
		soup = BeautifulSoup(r.text, 'lxml')
		count = 0
		for info in soup.findAll('a', href=True):
			website = website.strip()
			if(count < MAX_RESULTS and info['href'].strip().startswith(website)):
				links.append( info['href'])
				count += 1
				request = requests.get(info['href'], headers=headers)
				anotherSoup = BeautifulSoup(request.text, 'lxml')
				for image in anotherSoup.findAll('img'):
					try:
						if (len(image['src']) > 40 and ((".jpg" in image['src']) or (".jpeg" in image['src']) or (".png" in image['src'])) and "header" not in image['src'] and "icon" not in image['src'] and "logo" not in image['src'] and "navigasyon" not in image['src']):

							if(image['src'].startswith("//")):
								image['src'] = "https://" + image['src'][2:]
							if( "defacto" in image['src'] and "/6/" not in image['src']):
								continue
							images.append( image['src'])
							break		
					except Exception:
						a = 1
		return { "links": links, "imageLinks": images}
