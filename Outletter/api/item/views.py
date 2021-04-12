from io import BytesIO
from PIL import Image
import requests, uuid, cv2

from rest_framework import views, response, status

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile  
from django.conf import settings

from Outletter.api.item.serializers import QueryItemSerializer, QueryItemCreateSerializer,\
				ScrapedItemCreateSerializer, ScrapedItemUpdateSerializer, QueryItemUpdateSerializer,\
				ScrapingResponseSerializer
									
from Outletter.item.models import ScrapedItem, QueryItem

from src.similarity_engine import SimilarityEngine
from src.segmentation_engine import SegmentationEngine
from src.tagging_engine import TaggingEngine
from src.choices import GenderChoices, ShopChoices, LabelChoices
IMG_SIZE = (224,224)

class ItemListView(views.APIView):
	serializer_class = QueryItemCreateSerializer
	query_set = QueryItem.objects.all()

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
						'name': scraped_names[i],
						'price': scraped_prices[i],
						'url': scraped_urls[i],
						'image_url': scraped_image_links[i]
					}
				scraped_item_serializer = ScrapedItemCreateSerializer(data=image_data)
				if scraped_item_serializer.is_valid():
					scraped_item_serializer = scraped_item_serializer.save()
					scraped_items.append(scraped_item_serializer)

		return scraped_items

	def post(self, request, *args, **kwargs):
		item_serializer = self.serializer_class(data=request.data)
		if item_serializer.is_valid():
			query_item = item_serializer.save()
			res = self.run_engines(query_item)
			return response.Response(res, status=status.HTTP_200_OK)
		else:
			return response.Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	
	def apply_masks(images, outputs, labels):
		output_images = []
		output_labels = []
		for i in range(len(images)):
			img = images[i]
			instances = outputs[i]["instances"].to("cpu").get_fields()
			image_instances = len(instances['pred_classes'])
			if image_instances == 0:
				output_images.append(img)
				output_labels.append("None")
			else:
				img_scores = instances['scores']
				loc = np.argmax(img_scores)
				img_mask = instances['pred_masks'][loc]
				img = np.where(np.stack((img_mask,)*3, axis=-1) , img, 255)
				output_images.append(img)
				output_labels.append(labels[instances['pred_classes'][loc]])
		return output_images, output_labels
	
	def aspect_resize(src, tar_h, tar_w):
		h,w,c = src.shape
		max_dim = max(h,w)
		if max_dim == h:
			max_dim_name = 'h'
		else:
			max_dim_name = 'w'
		if max_dim_name == 'h':
			ratio = tar_h / h
		else:
			ratio = tar_w / w
		
		new_h = (int)(round(ratio * h))
		new_w = (int)(round(ratio * w))
		src = cv2.resize(src, (new_w, new_h))

		if max_dim_name == 'h':
			diff = (int)((tar_w - new_w) / 2)
			dest = cv2.copyMakeBorder(src, 0, 0, diff, tar_w - new_w - diff, cv2.BORDER_CONSTANT, 0)
		else:
			diff = (int)((tar_h - new_h) / 2)
			dest = cv2.copyMakeBorder(src, diff, tar_h - new_h - diff, 0, 0, cv2.BORDER_CONSTANT, 0)

		return dest
	
	def run_engines(self, query_item):
		# # Initialize the 3 engines required for processing
		# segmenter  = SegmentationEngine(settings.SEGEMENTATION_MODEL)
		# similarityEngine = SimilarityEngine(settings.SIMILARITY_MODEL)
		# tagger = TaggingEngine()

		# # Load the Query Image
		# queryImage = cv2.imread(query_item.picture.url[1:])
		
		# # Segment the query Image
		# segmented_queryImage, png_for_gcloud = segmenter.segment(queryImage, IMG_SIZE[0], IMG_SIZE[1])
		
		# # Save the segmented query image
		# png_for_cloud_name = query_item.picture.url[1:query_item.picture.url.rindex(".")] + ".png"
		# cv2.imwrite(query_item.picture.url[1:], segmented_queryImage)
		# cv2.imwrite(png_for_cloud_name, png_for_gcloud)

		# # Predict the label code and features for query Image
		# query_img_type_features, query_label_code = similarityEngine.predict_image(segmented_queryImage)
		# query_label = similarityEngine.decode_query_label(query_label_code)
		
		# # Do tagging on the segmented query image
		# scraped_urls, scraped_image_links, scraped_names, scraped_prices, scraped_genders, scraped_shops, tagged_texts, tagged_color = tagger.tagImage(
		# 	png_for_cloud_name, query_item.shop, query_item.for_gender, query_label)
		
		# # Update the label, text and color for the query items
		# data = {'texts': tagged_texts, 'color': tagged_color, 'label': query_label}
		# query_item_update_serializer = QueryItemUpdateSerializer(query_item, data=data)
		# if query_item_update_serializer.is_valid():
		# 	query_item = query_item_update_serializer.save()

		# # Create the scraped objects in the database
		# scraped_items = self.create_scraped_items_from_url(scraped_image_links, scraped_genders, 
		# 						scraped_shops, scraped_names, scraped_prices, scraped_urls)

		# # Read all scraped images
		# scraped_images = [cv2.resize(cv2.imread(item.picture.url[1:]), IMG_SIZE) for item in scraped_items]

		# # Segment all the scraped_images
		# segmented_scraped_images = [segmenter.segment(img, IMG_SIZE[0], IMG_SIZE[1])[0] for img in scraped_images]

		# # # Save and resize all scraped segmented images
		# # resized_segmented_scraped_images = []
		# # for i in range(len(segmented_scraped_images)):
		# # 	cv2.imwrite(scraped_items[i].picture.url[1:], segmented_scraped_images[i])

		# # Sort all segmented scraped images by similarity to the query image
		# given_img_type_features, given_img_type_labels = similarityEngine.predict_image(segmented_scraped_images)
		# sortedIndices, resultLabels = similarityEngine.sortSimilarity(query_img_type_features, query_label_code, given_img_type_features, given_img_type_labels)
		# sorted_scraped_items = [scraped_items[ind] for ind in sortedIndices]

		# # Update the label for the scraped items
		# for i in range(len(scraped_images)):
		# 	item = sorted_scraped_items[i]
		# 	data = {"label": resultLabels[i]}
		# 	scraped_item_update_serializer = ScrapedItemUpdateSerializer(item, data=data)
		# 	if scraped_item_update_serializer.is_valid():
		# 		sorted_scraped_items[i] = scraped_item_update_serializer.save()

		# # Serialize the response and return
		# return ScrapingResponseSerializer({'query_item': query_item, 'similar_items': sorted_scraped_items}).data
		return "bc"