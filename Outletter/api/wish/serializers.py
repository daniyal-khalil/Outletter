from Outletter.wish.models import Wish
from rest_framework import serializers
from Outletter.item.models import ScrapedItem

class WishCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wish
        fields = ('rel_item', )

    def create(self, validated_data):
        return Wish.objects.create(
            rel_item=validated_data['rel_item'],
            rel_user=self.context.get("request").user,
        )

class ScrapedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapedItem
        fields = '__all__'

    def to_representation(self, instance):
        result = super(ScrapedItemSerializer, self).to_representation(instance)
        if not self.context.get("debug", None):
            result.pop("label")
        return result

class WishDetailSerializer(serializers.ModelSerializer):
    rel_item = serializers.SerializerMethodField()

    def get_rel_item(self, obj):
        return ScrapedItemSerializer(obj.rel_item).data
    
    class Meta:
        model = Wish
        fields = ('id', 'rel_user', 'rel_item')