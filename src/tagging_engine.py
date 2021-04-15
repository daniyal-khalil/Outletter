import requests
from bs4 import BeautifulSoup
from google.cloud import vision
import io, os, random
from PIL import Image
import numpy as np

class TaggingEngine():
	def __init__(self):
		self.client = vision.ImageAnnotatorClient()

	def tagImage( self, img_name, shop, gender, label):
		content = None
		with io.open(img_name, 'rb') as image_file:
			content = image_file.read()
		
		image = vision.Image(content=content)
		texts = self.detect_text(image)
		dominant_colors = self.get_colors(image)
		label = label.replace("_", " ")
		
		if len(texts) > 0:
			searchQuery = "site:" + shop + " (" + label + ") and (" + gender + ") and (" + ' and '.join(dominant_colors) + ") and (" + ' '.join(texts) + ")"
		else:
			searchQuery = "site:" + shop + " (" + label + ") and (" + gender + ") and (" + ' and '.join(dominant_colors) + ")"
		print(searchQuery)
		
		links, imageLinks, names, prices, genders, shops = self.scrapeResults( searchQuery, shop, gender)
		return links, imageLinks, names, prices, genders, shops, texts, dominant_colors[0]
	
	def get_colors(self, image):
		response = self.client.image_properties(image=image)
		props = response.image_properties_annotation
		
		running_sum = 0
		vision_all_colors = []
		vision_scores = []
		for color in props.dominant_colors.colors:
			if running_sum > 80:
				break
			pixel_rounded = round(color.score*100)

			vision_all_colors.append([int(color.color.red),int(color.color.green),int(color.color.blue)])
			vision_scores.append(pixel_rounded)
		
		vision_all_colors = np.array(vision_all_colors)
		vision_scores = np.array(vision_scores)
		vision_colors = vision_all_colors[np.where(vision_scores >= 25)]

		color_dict = {'white': [255,255,255], 'black': [0,0,0], 'grey': [128,128,128], 'light blue': [0,0,255], 'light green': [0,255,0],
					'red': [255,0,0], 'yellow': [255,255,0], 'dark blue': [0,0,128], 'dark green': [0,128,0],
					'purple': [128,0,128], 'orange': [255,165,0], 'brown': [160,82,45], 'pink': [255,105,180]}

		colors = np.array(list(color_dict.values()))

		top_colors = []
		for top_color in vision_colors:
			top_color = list(top_color)
			color = np.array(top_color)
			distances = np.sqrt(np.sum((colors-color)**2,axis=1))
			index_of_smallest = np.where(distances==np.amin(distances))
			smallest_distance = colors[index_of_smallest][0]
			
			for k, v in color_dict.items():
				check = True
				for i in range(len(smallest_distance)):
					if smallest_distance[i] != v[i]:
						check = False
						break
				if check:
					top_colors.append(k)
		
		return list(set(top_colors))
	
	
	def detect_text(self, image):
		response = self.client.text_detection(image=image)
		texts = response.text_annotations
			
		vision_texts = set({})
		for text in texts:
			vision_texts.add(text.description.strip().replace("\n","").replace('@', 'O'))

		if response.error.message:
			raise Exception(
				'{}\nFor more info on error messages, check: '
				'https://cloud.google.com/apis/design/errors'.format(
					response.error.message))
					
		vision_texts = [] if len(list(vision_texts)) > 2 else list(vision_texts)
		return vision_texts

	def scrapeResults(self, query, website, gender):
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
		soup = BeautifulSoup(r.text, 'html.parser')
		
		MAX_RESULTS = 30
		count = 0
		links = []
		images = []
		names = []
		prices = []
		genders = []
		shops = []
		def get_link(link, start_sym, end_sym):
			start = link.find(start_sym, 0, len(link) - 1)+len(start_sym)
			end = link.find(end_sym, start, len(link) - 1)
			return link[start:end]
		
		for info in soup.findAll('a', href=True):
			link = get_link(info['href'], "q=", "&")
			if "%" in link:
				link = get_link(link, "", "%")
			image = info.findAll('img')
			if image and website in link:
				count += 1
				image = image[0]['src']
				links.append(link)
				images.append(image)
				names.append("temp")
				prices.append(19.99)
				genders.append(gender)
				shops.append(website)
			if count >= MAX_RESULTS:
				break
		return links, images, names, prices, genders, shops
