import requests
from bs4 import BeautifulSoup
from google.cloud import vision
import io, os, random
import webcolors
from scipy.spatial import KDTree

allowedTags = ["T-shirt", "Sweatshirt", "Jeans", "Sweater", "Jacket", "Coat", "Pants", "Trousers", "Shorts", "Shirt", "Blazer", "Vest", "Hoodie", "Skirt", "Blouse", "Sundress"]
colors = ["Blue", "Black", "Red", "White", "Grey", "Brown", "Yellow", "Orange", "Azure", "Purple", "Pink", "Green", "Violet"]
websites = ["www.koton.com", "www.lcwaikiki.com", "www.boyner.com.tr", "www.defacto.com.tr", "www.trendyol.com", "www2.hm.com/tr_tr"]


class TaggingEngine():
	def __init__(self):
		self.client = vision.ImageAnnotatorClient()


	def tagImage( self, img_name, shop, gender, label):
		content = None
		with io.open(img_name, 'rb') as image_file:
			content = image_file.read()
		
		image = vision.Image(content=content)
		texts = self.detect_text(image)
		dominant_colors = self.detect_color(image)
		if str(label) is 'Tshirts':
			label = 'T Shirts or tshirts or t-shirts or t shirts or T-shirts'

		searchQuery = "site:" + shop + " (" + label + ") and (" + gender + ") and (" + ' and '.join(dominant_colors) + ") and (" + ' '.join(texts) + ')'
		print(searchQuery)
		links, imageLinks, names, prices, genders, shops = self.scrapeResults( searchQuery, shop, gender)
		
		return links, imageLinks, names, prices, genders, shops, texts, dominant_colors[0]
	
	def detect_color(self, image):
		response = self.client.image_properties(image=image)
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
	
	
	def detect_text(self, image):
		response = self.client.text_detection(image=image)
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
		print(url)
		headers = {'user-agent': Agent}
		r = requests.get(url, headers=headers)
		soup = BeautifulSoup(r.text, 'html.parser')
		
		MAX_RESULTS = 15
		count = 0
		links = []
		images = []
		names = []
		prices = []
		genders = []
		shops = []
		
		for info in soup.findAll('a', href=True):
			link = info['href']
			link = "https://google.com" + link
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
		# 	website = website.strip()
		# 	if(count < MAX_RESULTS and info['href'].strip().startswith(website)):
		# 		links.append( info['href'])
		# 		count += 1
		# 		request = requests.get(info['href'], headers=headers)
		# 		anotherSoup = BeautifulSoup(request.text, 'lxml')
		# 		for image in anotherSoup.findAll('img'):
		# 			try:
		# 				if (len(image['src']) > 40 and ((".jpg" in image['src']) or (".jpeg" in image['src']) or (".png" in image['src'])) and "header" not in image['src'] and "icon" not in image['src'] and "logo" not in image['src'] and "navigasyon" not in image['src']):

		# 					if(image['src'].startswith("//")):
		# 						image['src'] = "https://" + image['src'][2:]
		# 					if( "defacto" in image['src'] and "/6/" not in image['src']):
		# 						continue
		# 					images.append( image['src'])
		# 					break		
		# 			except Exception:
		# 				a = 1
		return links, images, names, prices, genders, shops
