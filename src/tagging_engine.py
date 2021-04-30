import requests
from bs4 import BeautifulSoup
from google.cloud import vision
import io, os, random
from PIL import Image
import numpy as np
import time
from random import randint
import threading

class TaggingEngine():
	def __init__(self):
		self.client = vision.ImageAnnotatorClient()

	def tagImage( self, img_name, shop, gender, label):
		it = time.time()
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
		
		links, imageLinks, names, prices, genders, shops = self.scrapeResults( searchQuery, shop, gender, label)
		ft = time.time()
		print("tag TIme: " +  str(ft - it))
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
		if len(vision_colors) == 0:
			max_score_idx = np.argmax(vision_scores)
			vision_colors = [vision_all_colors[max_score_idx]]
		color_dict={'white':[255,255,255],'black':[0,0,0],'grey':[128,128,128],'lightblue':[114,188,212],
					'lightgreen':[44,238,144],'blue':[0,0,255],'green':[0,255,0],'darkblue':[0,0,128],
					'darkgreen':[0,100,0],'red':[255,0,0],'yellow':[255,255,0],'purple':[186,85,211],
					'orange':[255,165,0],'brown':[205,133,63],'pink':[255,105,180]} 

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
		biggest = ''
		len_biggest = 0
		for text in texts:
			if 'F@' in text.description.strip():
				return ['FOCUS']
			elif 'FO' in text.description.strip():
				return ['FOCUS']
			if len(text.description.strip()) > len_biggest:
				biggest = text.description.strip()
				len_biggest = len(biggest)
		temp_texts = biggest.split('\n')
		vision_texts = []
		for x in temp_texts:
			vision_texts.extend(x.split(' '))

		if response.error.message:
			raise Exception(
				'{}\nFor more info on error messages, check: '
				'https://cloud.google.com/apis/design/errors'.format(
					response.error.message))

		print(vision_texts)
		return vision_texts

	def scrapeResults(self, query, website, gender, label):
		query = query.replace(":", "%3A").replace(
		" ", "+").replace("/", "%2F").replace("@", "%40")
		text = '' + query
		url = 'https://www.google.com/search?q=' + text + '&hl=tr&source=lnms&tbm=isch'
		A = ("Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
			"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
			"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
			)
		Agent = A[random.randrange(len(A))]
		headers = {'user-agent': Agent}
		r = requests.get(url, headers=headers)
		soup = BeautifulSoup(r.text, 'html.parser')

		MAX_RESULTS = 10
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
			if image and website in link and link not in links:
				count += 1
				image = image[0]['src']
				links.append(link)
				images.append(image)
				names.append('')
				price = -1
				prices.append(price)
				genders.append(gender)
				shops.append(website)
			if count >= MAX_RESULTS:
				break
		return links, images, names, prices, genders, shops

	def scrape_names_threaded(self, links, website):
		prices = [None] * len(links)
		names = [None] * len(links)
		def getPrice(link, website="", index=0):
			try:
				A = ("Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
				"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
				"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
				)

				Agent = A[random.randrange(len(A))]
				headers = {'user-agent': Agent}
				r = requests.get(link, headers=headers)
				soup = BeautifulSoup(r.text, 'html.parser')
				if website == "www.koton.com":
					tag = soup.find('meta', {"name": "product:price:amount"})
					price = tag['content']
					tag = soup.find('meta', {"name": "og:title"})
					name = tag['content']

				if website == "www.trendyol.com":
					tag = soup.find('meta', {"name": "twitter:data1"})
					price = tag['content']
					tag = soup.find('meta', {"name": "description"})
					split = tag['content']
					split = split.split(' ')
					name = split[0] + " " + split[1] + " "  + split[2] + " " + split[3] + " " + split[4]

				if website == "www.lcwaikiki.com":
					tag = soup.find('span', {"class": "price"})
					price = tag.get_text()

				if website == "www.boyner.com.tr":
					tag = soup.find('p', {"class": "m-campaignPrice"})
					if (tag != None):
						price = tag.get_text()[:-3]
					else:
						tag = soup.find('ins', {"class": "price-payable"})
						price = tag.get_text()[:-3]
					tag = soup.find('meta', {"property": "og:title"})
				if (tag != None):
					name = tag['content']
					prices[index] = price
					names[index] = name
			except:
				prices[index] = -1
				names[index] = "_"
		
		def threads_price():
			for i in range(0,len(links)):
				first = threading.Thread(target=getPrice, args=(links[i], website, i))
				first.start()

			for i in range(0,len(links)):
				first.join()

		threads_price()

		for i in range(len(prices)):
			if prices[i] is None:
				prices[i] = -1
			if names[i] is None:
				names[i] = '_'

		return prices, names
