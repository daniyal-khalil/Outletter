from Outletter.item.models import Item
from Outletter.customerimageupload.models import CustomerImageUpload
from rest_framework import serializers

class ItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'price', 'url', 'picture']


class CustomerImageUploadSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model =  CustomerImageUpload
        fields = ['image','gender', 'shop', 'debug']