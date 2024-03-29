from io import BytesIO
from PIL import Image
import requests, uuid, cv2
import string, random 

from rest_framework import views, response, status, permissions
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile  
from django.conf import settings

from Outletter.api.item.serializers import QueryItemCreateSerializer,\
				ScrapedItemCreateSerializer, ScrapedItemUpdateSerializer, QueryItemUpdateSerializer,\
				ScrapingResponseSerializer, ScrapedItemSerializer, QuerySegmentInitialSerializer
									
from Outletter.item.models import ScrapedItem, QueryItem

from src.similarity_engine import SimilarityEngine
from src.segmentation_engine import SegmentationEngine
from src.tagging_engine import TaggingEngine
from src.choices import LabelChoicesQueried as lc
import time
IMG_SIZE = (224,224)

class ItemView(RetrieveModelMixin, GenericViewSet):
	serializer_class = ScrapedItemSerializer
	queryset = ScrapedItem.objects.all()
	permission_classes = (permissions.AllowAny,)
	lookup_field = "id"
	lookup_url_kwarg = "id"

class ItemListView(views.APIView):
	serializer_class = QueryItemCreateSerializer
	query_set = QueryItem.objects.all()
	permission_classes = (permissions.AllowAny,)

	def download_image(self, image_url):
		res = requests.get(image_url)
		content_type = res.headers.get('content-type', '')
		image_extension = content_type.split('/')[-1]
		image_name = uuid.uuid4().hex + '.' + image_extension
		image_io = BytesIO(res.content)
		image_io_content = ContentFile(image_io.getvalue())
		return InMemoryUploadedFile(image_io_content, None, image_name, content_type, image_io.tell, None)
	
	def create_scraped_items_from_url(self, scraped_image_links, scraped_gender, scraped_shop,
									scraped_names, scraped_prices, scraped_urls):
		scraped_items = []
		for i in range(len(scraped_image_links)):
			image_file = self.download_image(scraped_image_links[i])
			if image_file:
				image_data = {
						'picture': image_file,
						'gender': scraped_gender[i],
						'shop': scraped_shop[i],
						'name': '_' if scraped_names[i] == '' else scraped_names[i],
						'price': scraped_prices[i],
						'url': scraped_urls[i],
						'image_url': scraped_image_links[i]
					}
				scraped_item_serializer = ScrapedItemCreateSerializer(data=image_data)
				if scraped_item_serializer.is_valid():
					scraped_item_serializer = scraped_item_serializer.save()
					scraped_items.append(scraped_item_serializer)
				else:
					print(scraped_item_serializer.errors)

		return scraped_items

	def generate_random_string(self, N=10):
		return ''.join(random.choices(string.ascii_uppercase + string.digits, k=N)) 

	def get(self, request, *args, **kwargs):
		st = time.time()
		if 'id' not in request.GET or 'image_name' not in request.GET or 'label' not in request.GET:
			return response.Response('GET not allowed in the following format', status=status.HTTP_400_BAD_REQUEST)
		id = request.GET.get('id')
		image_name = request.GET.get('image_name')
		label = request.GET.get('label')
		query_item = QueryItem.objects.filter(pk=id).first()
		res = self.process_segmented(query_item, image_name, label)
		ft = time.time()
		print("TIME: ", ft - st)
		return response.Response(res, status=status.HTTP_200_OK)

	def post(self, request, *args, **kwargs):
		start = time.time()
		item_serializer = self.serializer_class(data=request.data)
		if item_serializer.is_valid():
			query_item = item_serializer.save()
			print("before seg: ", time.time() - start)
			res = self.segment_query(query_item)
			print("TIME: ", time.time() - start)
			return response.Response(res, status=status.HTTP_200_OK)
		else:
			return response.Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	
	def segment_query(self, query_item):
		# Initialize the segmenter only
		segmenter  = SegmentationEngine(settings.SEGMENTATION_MODEL)

		# Load the Query Image
		queryImage = cv2.imread(query_item.picture.url[1:])

		# Create and query items array
		segmented_items_names_labels = []

		# Segment the query Image
		try:
			segmented_images = segmenter.segment(queryImage, IMG_SIZE[0], IMG_SIZE[1], query=True)
			st_1 = time.time()
		except:
			print("No cloth instance found")
			return ScrapingResponseSerializer({'query_item': query_item, 'similar_items': []}).data
		
		if len(segmented_images) == 1:
			return self.run_engines_single(query_item, segmented_images[0], segmenter)
		elif len(segmented_images) > 1:
			st_2 = time.time()
			for segmented_queryImage, segmented_queryImage_label, segmented_queryImage_png, segmented_queryImage_trans_png in segmented_images:
				# Save the segmented query image
				random_name = self.generate_random_string()
				cv2.imwrite("./media/item_pictures/" + random_name + ".jpg", segmented_queryImage)
				cv2.imwrite("./media/item_pictures/" + random_name + ".png", segmented_queryImage_png)
				cv2.imwrite("./media/item_pictures/" + random_name + "_trans.png", segmented_queryImage_trans_png)
				segmented_items_names_labels.append(("/media/item_pictures/" + random_name + "_trans.png", segmented_queryImage_label))
				st_3 = time.time()
				st_2 = st_3

			return_result = QuerySegmentInitialSerializer(query_item, context={"seg_labels_imgs": segmented_items_names_labels}).data
			return return_result

	def process_segmented(self, query_item, image_name, label):
		segmenter  = SegmentationEngine(settings.SEGMENTATION_MODEL)
		similarityEngine = SimilarityEngine(settings.SIMILARITY_MODEL)
		tagger = TaggingEngine()

		# Load the Query Image
		queryImage = cv2.imread(image_name[1:image_name.rindex(".")][:-6] + ".jpg")

		# Save the segmented query image
		png_for_cloud_name = image_name[1:image_name.rindex(".")][:-6] + ".png"
		cv2.imwrite(query_item.picture.url[1:], queryImage)

		# Predict the features for query Image
		query_img_type_features, query_label_code = similarityEngine.predict_image(queryImage)

		# Do tagging on the segmented query image
		scraped_urls, scraped_image_links, scraped_names, scraped_prices, scraped_genders, scraped_shops, tagged_texts, tagged_color = tagger.tagImage(
		png_for_cloud_name, query_item.shop, query_item.for_gender, label)

		if len(scraped_urls) == 0:
			print("Could not perform scraping")
			return ScrapingResponseSerializer({'query_item': query_item, 'similar_items': []}).data

		# Update the label, text and color for the query items
		data = {'texts': tagged_texts, 'color': tagged_color, 'label': label}
		query_item_update_serializer = QueryItemUpdateSerializer(query_item, data=data)
		if query_item_update_serializer.is_valid():
			query_item = query_item_update_serializer.save()

		# Create the scraped objects in the database
		scraped_items = self.create_scraped_items_from_url(scraped_image_links, scraped_genders, 
								scraped_shops, scraped_names, scraped_prices, scraped_urls)

		# Read all scraped images
		# scraped_images = [segmenter.aspect_resize(cv2.imread(item.picture.url[1:]), IMG_SIZE[0], IMG_SIZE[1]) for item in scraped_items]
		scraped_images = [cv2.imread(item.picture.url[1:]) for item in scraped_items]

		if len(scraped_images) == 0:
			print("could not create scraped items")
			return ScrapingResponseSerializer({'query_item': query_item, 'similar_items': []}).data

		# Segment all the scraped_images
		segmented_scraped_images = []
		scraped_image_items = []
		given_img_type_labels = []
		list_segmented_tuples = segmenter.segment(scraped_images, IMG_SIZE[0], IMG_SIZE[1], prev_label=label)
		for i, img in enumerate(list_segmented_tuples):
			try:
				segmented_scraped_images.append(img[0])
				scraped_image_items.append(scraped_items[i])
				given_img_type_labels.append(img[1])
			except:
				print('Empty Image Encountered')

		if len(segmented_scraped_images) == 0:
			print("could not segment any scraped  items")
			return ScrapingResponseSerializer({'query_item': query_item, 'similar_items': []}).data

		# Save all scraped segmented images
		for i in range(len(segmented_scraped_images)):
			cv2.imwrite(scraped_image_items[i].picture.url[1:], segmented_scraped_images[i])

		# Sort all segmented scraped images by similarity to the query image
		given_img_type_features, given_img_type_labels_waste = similarityEngine.predict_image(segmented_scraped_images)
		sortedIndices, resultLabels = similarityEngine.sortSimilarity(label, query_img_type_features, given_img_type_features, given_img_type_labels)
		sorted_scraped_items = [scraped_image_items[ind] for ind in sortedIndices]

		# Update the label for the scraped items
		for i in range(len(scraped_image_items)):
			item = sorted_scraped_items[i]
			data = {"name": str("_"), "price": float(-1), "label": resultLabels[i]}
			scraped_item_update_serializer = ScrapedItemUpdateSerializer(item, data=data)
			if scraped_item_update_serializer.is_valid():
				sorted_scraped_items[i] = scraped_item_update_serializer.save()
		
		# # Remove duplicate items if being returned
		# url_set = [i.url for j, i in enumerate(sorted_scraped_items)]
		# sorted_scraped_items = [i for j, i in enumerate(sorted_scraped_items) if i.url not in url_set[:j]]
		
		# Serialize the response and return
		return ScrapingResponseSerializer({'query_item': query_item, 'similar_items': sorted_scraped_items}).data

	def run_engines_single(self, query_item, segmented_results, segmenter):
		# Initialize the 3 engines required for processing
		similarityEngine = SimilarityEngine(settings.SIMILARITY_MODEL)
		tagger = TaggingEngine()

		# Save the segmented query image
		png_for_cloud_name = query_item.picture.url[1:query_item.picture.url.rindex(".")] + ".png"
		cv2.imwrite(query_item.picture.url[1:], segmented_results[0])
		cv2.imwrite(png_for_cloud_name, segmented_results[2])

		# Predict the features for query Image
		query_img_type_features, query_label_code = similarityEngine.predict_image(segmented_results[0])
		
		# Do tagging on the segmented query image
		scraped_urls, scraped_image_links, scraped_names, scraped_prices, scraped_genders, scraped_shops, tagged_texts, tagged_color = tagger.tagImage(
			png_for_cloud_name, query_item.shop, query_item.for_gender, segmented_results[1])

		if len(scraped_urls) == 0:
			print("could not perform scraping")
			return ScrapingResponseSerializer({'query_item': query_item, 'similar_items': []}).data

		# Update the label, text and color for the query items
		data = {'texts': tagged_texts, 'color': tagged_color, 'label': segmented_results[1]}
		query_item_update_serializer = QueryItemUpdateSerializer(query_item, data=data)
		if query_item_update_serializer.is_valid():
			query_item = query_item_update_serializer.save()

		# Create the scraped objects in the database
		scraped_items = self.create_scraped_items_from_url(scraped_image_links, scraped_genders, 
								scraped_shops, scraped_names, scraped_prices, scraped_urls)

		# Read all scraped images
		# scraped_images = [segmenter.aspect_resize(cv2.imread(item.picture.url[1:]), IMG_SIZE[0], IMG_SIZE[1]) for item in scraped_items]
		scraped_images = [cv2.imread(item.picture.url[1:]) for item in scraped_items]
		
		if len(scraped_images) == 0:
			print("could not create scraped items")
			return ScrapingResponseSerializer({'query_item': query_item, 'similar_items': []}).data
		# # Temporarily until segmenter is fast
		# segmented_scraped_images = scraped_images
		# Segment all the scraped_images
		segmented_scraped_images = []
		scraped_image_items = []
		given_img_type_labels = []
		list_segmented_tuples = segmenter.segment(scraped_images, IMG_SIZE[0], IMG_SIZE[1], prev_label=segmented_results[1])
		for i, img in enumerate(list_segmented_tuples):
			try:
				segmented_scraped_images.append(img[0])
				given_img_type_labels.append(img[1])
				scraped_image_items.append(scraped_items[i])
			except:
				print('Empty Image Encountered')

		if len(segmented_scraped_images) == 0:
			print("could not segment any scraped  items")
			return ScrapingResponseSerializer({'query_item': query_item, 'similar_items': []}).data

		# Save all scraped segmented images
		for i in range(len(segmented_scraped_images)):
			cv2.imwrite(scraped_image_items[i].picture.url[1:], segmented_scraped_images[i])

		# Sort all segmented scraped images by similarity to the query image
		given_img_type_features, waste = similarityEngine.predict_image(segmented_scraped_images)
		sortedIndices, resultLabels = similarityEngine.sortSimilarity(segmented_results[1], query_img_type_features, given_img_type_features, given_img_type_labels)
		sorted_scraped_items = [scraped_image_items[ind] for ind in sortedIndices]

		# Update the label for the scraped items
		for i in range(len(scraped_image_items)):
			item = sorted_scraped_items[i]
			data = {"name": str("_"), "price": float(-1), "label": resultLabels[i]}
			scraped_item_update_serializer = ScrapedItemUpdateSerializer(item, data=data)
			if scraped_item_update_serializer.is_valid():
				sorted_scraped_items[i] = scraped_item_update_serializer.save()
		
		# # Remove duplicate items if being returned
		# url_set = [i.url for j, i in enumerate(sorted_scraped_items)]
		# sorted_scraped_items = [i for j, i in enumerate(sorted_scraped_items) if i.url not in url_set[:j]]
		
		# Serialize the response and return
		return ScrapingResponseSerializer({'query_item': query_item, 'similar_items': sorted_scraped_items}).data

class ItemInfoView(views.APIView):
	serializer_class = QueryItemCreateSerializer
	query_set = QueryItem.objects.all()
	permission_classes = (permissions.AllowAny,)

	def get(self, request, *args, **kwargs):
		st = time.time()
		if 'query_id' not in request.GET or 'similar_id' not in request.GET:
			return response.Response('GET not allowed in the following format', status=status.HTTP_400_BAD_REQUEST)
		
		query_id = request.GET.get('query_id')
		similar_id = request.GET.get('similar_id')
		

		similar_items_ids = similar_id.split(",")
		similar_items_id = [int(x.strip()) for x in similar_items_ids]

		scraped_items = ScrapedItem.objects.filter(pk__in=similar_items_id)
		links = [item.url for item in scraped_items]
		query_item = QueryItem.objects.filter(pk=query_id).first()
		website = query_item.shop
		tagger = TaggingEngine()

		final_scraped_items = []
		prices, names = tagger.scrape_names_threaded(links, website)
		print(prices,names)
		for i in range(len(scraped_items)):
			item = scraped_items[i]
			data = {"name": str(names[i]), "price": float(prices[i]), "label": scraped_items[i].label}
			scraped_item_update_serializer = ScrapedItemUpdateSerializer(item, data=data)
			if scraped_item_update_serializer.is_valid():
				final_scraped_items.append(scraped_item_update_serializer.save())
			else:
				print(scraped_item_update_serializer.errors)
		ft = time.time()
		return_result = ScrapingResponseSerializer({'query_item': query_item, 'similar_items': final_scraped_items}).data
		print("MultithreadedScraping Time: ", ft - st)
		return response.Response(return_result, status=status.HTTP_200_OK)

class ItemListTestView(views.APIView):
	serializer_class = QueryItemCreateSerializer
	query_set = QueryItem.objects.all()

	def post(self, request, *args, **kwargs):
		item_serializer = self.serializer_class(data=request.data)
		if item_serializer.is_valid():
			query_item = item_serializer.save()
			sorted_scraped_items = ScrapedItem.objects.all()[:15]
			res = ScrapingResponseSerializer({'query_item': query_item, 'similar_items': sorted_scraped_items}).data
			return response.Response(res, status=status.HTTP_200_OK)
		else:
			return response.Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
