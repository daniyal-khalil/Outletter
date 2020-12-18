from rest_framework import views, response, status

from Outletter.api.item.serializers import ItemSerializer
from Outletter.item.models import Item


class ItemListView(views.APIView):
    serializer_class = ItemSerializer

    def get(self, request, format=None):
        items = Item.objects.all()
        serialized_items = ItemSerializer(items, many=True).data
        return response.Response(serialized_items)
