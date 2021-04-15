from Outletter.item.models import ScrapedItem, QueryItem
from django.contrib.postgres.fields import ArrayField
from rest_framework import serializers

from src.choices import GenderChoices, ShopChoices, LabelChoicesQueried, LabelChoicesScraped

class QueryItemCreateSerializer(serializers.ModelSerializer):
    gender = serializers.ChoiceField(required=True, source='for_gender', choices=GenderChoices.choices)
    picture = serializers.ImageField(required=True)
    debug = serializers.BooleanField(required=True)
    shop = serializers.ChoiceField(required=True, choices=ShopChoices.choices)
    
    class Meta:
        model = QueryItem
        fields = ('picture', 'gender', 'shop', 'debug')

    def create(self, validated_data):
        return QueryItem.objects.create(
            for_gender=validated_data['for_gender'],
            picture=validated_data['picture'],
            shop=validated_data['shop'],
            debug=validated_data['debug'],
        )

class QueryItemUpdateSerializer(serializers.ModelSerializer):
    color = serializers.CharField(required=True)
    label = serializers.ChoiceField(required=True, choices=LabelChoicesQueried.choices)
    texts = ArrayField(serializers.CharField())

    class Meta:
        model = QueryItem
        fields = ("color", "texts", "label")
    
    def update(self, instance, validated_data):
        instance.color = validated_data.get('color', instance.color)
        instance.texts = validated_data.get('texts', instance.texts)
        instance.label = validated_data.get('label', instance.label)
        instance.save()
        return instance

class QueryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryItem
        fields = '__all__'

class ScrapedItemCreateSerializer(serializers.ModelSerializer):
    gender = serializers.ChoiceField(required=True, source='for_gender', choices=GenderChoices.choices)
    picture = serializers.ImageField(required=True)
    shop = serializers.ChoiceField(required=True, choices=ShopChoices.choices)
    name = serializers.CharField(required=True)
    price = serializers.DecimalField(required=True, max_digits=6, decimal_places=2)
    url = serializers.URLField(required=True)
    image_url = serializers.URLField(required=True)
    
    class Meta:
        model = ScrapedItem
        fields = ('picture', 'gender', 'shop', 'name', 'price', 'url', 'image_url')
        
    def create(self, validated_data):
        return ScrapedItem.objects.create(
            for_gender=validated_data['for_gender'],
            picture=validated_data['picture'],
            shop=validated_data['shop'],
            name=validated_data['name'],
            price=validated_data['price'],
            url=validated_data['url'],
            image_url=validated_data['image_url'],
        )
    
class ScrapedItemUpdateSerializer(serializers.ModelSerializer):
    label = serializers.ChoiceField(required=True, choices=LabelChoicesScraped.choices)

    class Meta:
        model = ScrapedItem
        fields = ("label", )
    
    def update(self, instance, validated_data):
        instance.label = validated_data.get('label', instance.label)
        instance.save()
        return instance

class ScrapedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapedItem
        fields = '__all__'

    def to_representation(self, instance):
        result = super(ScrapedItemSerializer, self).to_representation(instance)
        if not self.context.get("debug", None):
            result.pop("label")
        return result

class ScrapingResponseSerializer(serializers.Serializer):
    query_item = serializers.SerializerMethodField()
    similar_items = serializers.SerializerMethodField()

    class Meta:
        fields = ("query_item", "similar_items")
    
    def get_query_item(self, obj):
        return QueryItemSerializer(obj.get('query_item')).data
    
    def get_similar_items(self, obj):
        similar_items = obj.get('similar_items')
        query_item = obj.get('query_item')
        serialized_items = []
        for item in similar_items:
            serialized_items.append(
                ScrapedItemSerializer(item, context={'debug': query_item.debug}).data)
        return serialized_items
    
    def to_representation(self, instance):
        result = super(ScrapingResponseSerializer, self).to_representation(instance)
        if not result["query_item"]["debug"]:
            result.pop("query_item")
        return result