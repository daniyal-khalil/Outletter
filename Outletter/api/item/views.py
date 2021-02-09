from io import BytesIO
from PIL import Image
import requests
import base64
import cv2
import os

from rest_framework import views, response, status

from django.conf import settings

from Outletter.api.item.serializers import QueryItemSerializer, QueryItemCreateSerializer
from Outletter.item.models import ScrapedItem, QueryItem

from src.similarity_engine import SimilarityEngine
from src.segmentation_engine import SegmentationEngine
from src.tagging_engine import TaggingEngine

IMG_SIZE = (224,224)

class ItemListView(views.APIView):
	serializer_class = QueryItemCreateSerializer
	query_set = QueryItem.objects.all()

	def post(self, request, format=None):
		item_serializer = self.serializer_class(data=request.data)
		if item_serializer.is_valid():
			item_serializer.save()
			res = self.run_engines(item_serializer)
			return response.Response(res, status=status.HTTP_200_OK)
		else:
			return response.Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def run_engines(self, item_serializer):
		# Initialize the 3 engines required for processing
		segmenter  = SegmentationEngine(settings.SEGEMENTATION_MODEL)
		similarityEngine = SimilarityEngine(settings.SIMILARITY_MODEL)
		tagger = TaggingEngine()

		# Load the Query Image
		queryImage = cv2.imread(item_serializer.data['picture'][1:])
		
		# Segment the query Image
		segmented_queryImage = segmenter.get_dress(queryImage, IMG_SIZE[0], IMG_SIZE[1])
		
		# Save the segmented query image
		cv2.imwrite(item_serializer.data['picture'][1:], segmented_queryImage)

		# Resize the segmented query image
		resized_segmented_queryImage = cv2.resize(segmented_queryImage, IMG_SIZE)

		# Predict the label code and features for query Image
		query_img_type_features, query_label_code = similarityEngine.predict_image(resized_segmented_queryImage)
		query_label = similarityEngine.decode_query_label(query_label_code)
		
		# # Do tagging on the segmented query image
		scraped_urls, scraped_image_links, tagged_texts, tagged_colors, tagged_labels = tagger.tagImage(
			resized_segmented_queryImage, item_serializer.data['shop'], item_serializer.data['gender'], query_label)
				
		
		return 'query_label'

# def readImages(folder):
# 	images = []
# 	for filename in os.listdir(folder):
# 		img = cv2.imread(os.path.join(folder,filename))
# 		output = cv2.resize(img, IMG_SIZE)
# 		images.append(output)
# 	return images
	
# def downloadImages(folder, links):
# 	if os.path.exists(folder):
# 		os.system("rm -r " + folder)
# 	os.mkdir(folder)
# 	idx = 0
# 	for link in links:
# 		idx += 1
# 		response = requests.get(link)
# 		img = Image.open(BytesIO(response.content))
# 		img.save(os.path.join(folder, str(idx) + '.' + link.split('.')[-1]))

# class CustomerImageUploadView(views.APIView):
# 	serializer_class = CustomerImageUploadSerializer

# 	def get(self, request, format=None):
# 		uploadedImage = CustomerImageUpload.objects.all()
# 		serialized_items = CustomerImageUploadSerializer(uploadedImage, many=True).data
# 		return response.Response(serialized_items)  

# 	def post(self, request, format=None):
# 		image = request.FILES['image'].read()
# 		name = request.FILES['image'].name
# 		shop = int(request.POST.get('shop', 0))
# 		debug = True if request.POST.get('debug', '') == 'true' else False
# 		imagepath = os.path.join(settings.MEDIA_ROOT, name)
# 		with open( imagepath, 'wb') as f:
# 			f.write(image)
		
# 		###running code
# 		segmenter  = SegmentationEngine(settings.SEGEMENTATION_MODEL)
# 		segmentedImage = segmenter.get_dress(imagepath)
# 		segmentedImageName = os.path.join(settings.MEDIA_ROOT, ''.join(name.split('.')[:-1]) + '_segmented.png')
# 		cv2.imwrite(segmentedImageName, segmentedImage)
# 		segmentedImage = cv2.imread(segmentedImageName)
# 		segmentedImage = cv2.resize(segmentedImage, IMG_SIZE)
# 		base64SegmentedImage = None
		
# 		with open(segmentedImageName, "rb") as image_file:
# 			base64SegmentedImage = base64.b64encode(image_file.read()).decode('utf-8')
		
# 		similarityEngine = SimilarityEngine(settings.SIMILARITY_MODEL)
# 		queryLabel2 = similarityEngine.predict(segmentedImage)
		
# 		tagger = TaggingEngine(segmentedImageName)
# 		gender = 'male' if request.POST.get('gender', '') == 'm' else 'female'
# 		tagresult = tagger.tagImage(shop,gender,queryLabel2,True)
# 		resultLinks = tagresult.get("links", [])
# 		resultImageLinks = tagresult.get("imageLinks", [])
# 		resultTexts = tagresult.get("texts",[])
# 		resultColors = tagresult.get("colors",[])
# 		resultTags = tagresult.get("tags",[])
		
# 		resultImagesPath = os.path.join(settings.MEDIA_ROOT, 'customer_id_result')
# 		downloadImages(resultImagesPath,resultImageLinks)
		
# 		#segment downloaded images
		
# 		resultImages = readImages(resultImagesPath)
		
# 		sortedIndices, resultLabels, queryLabel = similarityEngine.sortSimilarity(segmentedImage, resultImages)
		
# 		sortedImageLinks = []
# 		sortedLinks = []
# 		for x in range(len(sortedIndices)):
# 			sortedImageLinks.append(resultImageLinks[sortedIndices[x]])
# 			sortedLinks.append(resultLinks[sortedIndices[x]])
# 		data = {}
# 		if not debug:
# 			data = {
# 				'links': sortedLinks,
# 				'imageLinks': sortedImageLinks
# 			}
# 		else:
# 			data = {
# 				'tags': resultTags,
# 				'text': resultTexts,
# 				'colors': resultColors,
# 				'imageLinks': sortedImageLinks,
# 				'links': sortedLinks,
# 				'queryLabel': queryLabel,
# 				'resultLabels': resultLabels,
# 				'segmented_image': base64SegmentedImage,
# 			}
# 		return JsonResponse(data)

