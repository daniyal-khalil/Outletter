from rest_framework import views, response, status
import os
from django.http import JsonResponse
from django.conf import settings
import cv2
from Outletter.api.item.serializers import ItemSerializer, CustomerImageUploadSerializer
from Outletter.item.models import Item
from PIL import Image
import requests
import base64
from io import BytesIO

from Outletter.customerimageupload.models import CustomerImageUpload
from src.similarity_engine import SimilarityEngine
from src.segmentation_engine import SegmentationEngine
from src.tagging_engine import TaggingEngine

IMG_SIZE = (224,224)

class ItemListView(views.APIView):
	serializer_class = ItemSerializer

	def get(self, request, format=None):
		items = Item.objects.all()
		serialized_items = ItemSerializer(items, many=True).data
		return response.Response(serialized_items)

	def post(self, request, format=None):
		data = {
			'name': 'Vitor',
			'location': 'Finland',
			'is_active': True,
			'count': 28
		}
		return JsonResponse(data)

def readImages(folder):
	images = []
	for filename in os.listdir(folder):
		img = cv2.imread(os.path.join(folder,filename))
		output = cv2.resize(img, IMG_SIZE)
		images.append(output)
	return images
	
def downloadImages(folder, links):
	if os.path.exists(folder):
		os.system("rm -r " + folder)
	os.mkdir(folder)
	idx = 0
	for link in links:
		idx += 1
		response = requests.get(link)
		img = Image.open(BytesIO(response.content))
		img.save(os.path.join(folder, str(idx) + '.' + link.split('.')[-1]))

class CustomerImageUploadView(views.APIView):
	serializer_class = CustomerImageUploadSerializer

	def get(self, request, format=None):
		uploadedImage = CustomerImageUpload.objects.all()
		serialized_items = CustomerImageUploadSerializer(uploadedImage, many=True).data
		return response.Response(serialized_items)  

	def post(self, request, format=None):
		image = request.FILES['image'].read()
		name = request.FILES['image'].name
		shop = int(request.POST.get('shop', 0))
		debug = True if request.POST.get('debug', '') == 'true' else False
		imagepath = os.path.join(settings.MEDIA_ROOT, name)
		with open( imagepath, 'wb') as f:
			f.write(image)
		
		###running code
		segmenter  = SegmentationEngine(settings.SEGEMENTATION_MODEL)
		segmentedImage = segmenter.get_dress(imagepath)
		segmentedImageName = os.path.join(settings.MEDIA_ROOT, ''.join(name.split('.')[:-1]) + '_segmented.png')
		cv2.imwrite(segmentedImageName, segmentedImage)
		segmentedImage = cv2.imread(segmentedImageName)
		segmentedImage = cv2.resize(segmentedImage, IMG_SIZE)
		base64SegmentedImage = None
		
		with open(segmentedImageName, "rb") as image_file:
			base64SegmentedImage = base64.b64encode(image_file.read()).decode('utf-8')
		
		similarityEngine = SimilarityEngine(settings.SIMILARITY_MODEL)
		queryLabel2 = similarityEngine.predict(segmentedImage)
		
		tagger = TaggingEngine(segmentedImageName)
		gender = 'male' if request.POST.get('gender', '') == 'm' else 'female'
		tagresult = tagger.tagImage(shop,gender,queryLabel2,True)
		resultLinks = tagresult.get("links", [])
		resultImageLinks = tagresult.get("imageLinks", [])
		resultTexts = tagresult.get("texts",[])
		resultColors = tagresult.get("colors",[])
		resultTags = tagresult.get("tags",[])
		
		resultImagesPath = os.path.join(settings.MEDIA_ROOT, 'customer_id_result')
		downloadImages(resultImagesPath,resultImageLinks)
		
		#segment downloaded images
		
		resultImages = readImages(resultImagesPath)
		
		sortedIndices, resultLabels, queryLabel = similarityEngine.sortSimilarity(segmentedImage, resultImages)
		
		sortedImageLinks = []
		sortedLinks = []
		for x in range(len(sortedIndices)):
			sortedImageLinks.append(resultImageLinks[sortedIndices[x]])
			sortedLinks.append(resultLinks[sortedIndices[x]])
		data = {}
		if not debug:
			data = {
				'links': sortedLinks,
				'imageLinks': sortedImageLinks
			}
		else:
			data = {
				'tags': resultTags,
				'text': resultTexts,
				'colors': resultColors,
				'imageLinks': sortedImageLinks,
				'links': sortedLinks,
				'queryLabel': queryLabel,
				'resultLabels': resultLabels,
				'segmented_image': base64SegmentedImage,
			}
		return JsonResponse(data)

