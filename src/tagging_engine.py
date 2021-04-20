import requests
from bs4 import BeautifulSoup
from google.cloud import vision
import io, os, random
import webcolors
from scipy.spatial import KDTree

# allowedTags = ["T-shirt", "Sweatshirt", "Jeans", "Sweater", "Jacket", "Coat", "Pants", "Trousers", "Shorts", "Shirt", "Blazer", "Vest", "Hoodie", "Skirt", "Blouse", "Sundress"]
# colors = ["Blue", "Black", "Red", "White", "Grey", "Brown", "Yellow", "Orange", "Azure", "Purple", "Pink", "Green", "Violet"]
# websites = ["www.koton.com", "www.lcwaikiki.com", "www.boyner.com.tr", "www.defacto.com.tr", "www.trendyol.com", "www2.hm.com/tr_tr"]


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

	def getPrice(link, website=""):
		A = ("Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
			"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
			"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
			)

		Agent = A[random.randrange(len(A))]
		headers = {'user-agent': Agent}
		r = requests.get(link, headers=headers)
		soup = BeautifulSoup(r.text, 'html.parser')
		price = ""
		name = ""

		if website == "www.koton.com":
		tag = soup.find('meta', {"name": "product:price:amount"})
		price = tag['content']
		tag = soup.find('meta', {"name": "og:title"})
		name = tag['content']
		return price, name

		if website == "www.trendyol.com":
		tag = soup.find('meta', {"name": "twitter:data1"})
		price = tag['content']
		tag = soup.find('meta', {"name": "description"})
		split = tag['content']
		split = split.split(' ')
		name = split[0] + " " + split[1] + " "  + split[2] + " " + split[3] + " " + split[4]
		print(type(split))
		print(split)
		return price, name

		if website == "www.lcwaikiki.com":
		tag = soup.find('span', {"class": "price"})
		price = tag.get_text()

		return price, name

		if website == "www.boyner.com.tr":
		tag = soup.find('p', {"class": "m-campaignPrice"})
		if (tag != None):
			print(tag.get_text())
			price = tag.get_text()[:-3]
		else:
			tag = soup.find('ins', {"class": "price-payable"})
			price = tag.get_text()[:-3]
		tag = soup.find('meta', {"property": "og:title"})
		if (tag != None):
			name = tag['content']

		return price, name



	def scrapeResults(query, website, gender):
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
		start = link.find("q=", 0, len(link) - 1)+len("q=")
		end = link.find("&", start, len(link) - 1)
		link = link[start:end]
		link = link.split('%')[0]
		image = info.findAll('img')
		if image and website in link:
			count += 1
			image = image[0]['src']
			price, name = getPrice(link, website)
			if (price != "" and name != ""):
			links.append(link)
			images.append(image)
			names.append(name)
			prices.append(price)
			genders.append(gender)
			shops.append(website)
			count -=1
		if count >= MAX_RESULTS:
			break
		return links, images, names, prices, genders, shops
