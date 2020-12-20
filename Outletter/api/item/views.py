from rest_framework import views, response, status

from Outletter.api.item.serializers import ItemSerializer
from Outletter.item.models import Item
from src.similarity_engine import SimilarityEngine

class ItemListView(views.APIView):
    serializer_class = ItemSerializer

    def get(self, request, format=None):
        similarityEngine = SimilarityEngine(None)
        similarityEngine.check()
        items = Item.objects.all()
        serialized_items = ItemSerializer(items, many=True).data
        return response.Response(serialized_items)
