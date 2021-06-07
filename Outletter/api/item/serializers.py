from Outletter.item.models import ScrapedItem, QueryItem
from Outletter.review.models import Review
from Outletter.api.review.serializers import ReviewDetailSerializer
from Outletter.like.models import Like
from Outletter.wish.models import Wish
from django.contrib.postgres.fields import ArrayField
from rest_framework import serializers

from src.choices import GenderChoices, ShopChoices, LabelChoicesQueried

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
    label = serializers.ChoiceField(required=True, choices=LabelChoicesQueried.choices)
    name = serializers.CharField(required=True)
    price = serializers.DecimalField(required=True, max_digits=6, decimal_places=2)

    class Meta:
        model = ScrapedItem
        fields = ("label", 'name','price')
    
    def update(self, instance, validated_data):
        instance.label = validated_data.get('label', instance.label)
        instance.name = validated_data.get('name', instance.name)
        instance.price = validated_data.get('price', instance.price)
        instance.save()
        return instance

class ScrapedItemSerializer(serializers.ModelSerializer):
    item_reviews = serializers.SerializerMethodField()
    item_likes_count = serializers.SerializerMethodField()
    item_wish_count = serializers.SerializerMethodField()

    class Meta:
        model = ScrapedItem
        fields = '__all__'

    def to_representation(self, instance):
        result = super(ScrapedItemSerializer, self).to_representation(instance)
        if not self.context.get("debug", None):
            result.pop("label")
        return result
    
    def get_item_reviews(self, obj):
        return ReviewDetailSerializer(Review.objects.filter(rel_item=obj), many=True).data
    
    def get_item_likes_count(self, obj):
        return Like.objects.filter(rel_item=obj).count()
    
    def get_item_wish_count(self, obj):
        return Wish.objects.filter(rel_item=obj).count()

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

class QueryOptionSerializer(serializers.Serializer):
    image_name = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()

    class Meta:
        fields = ("image_name", "label")
    
    def get_image_name(self, obj):
        return obj[0]
    
    def get_label(self, obj):
        return obj[1]

class QuerySegmentInitialSerializer(serializers.Serializer):
    n = serializers.SerializerMethodField()
    query_item = serializers.SerializerMethodField()
    options = serializers.SerializerMethodField()

    class Meta:
        fields = ("n", "query_item", "options")
    
    def get_n(self, obj):
        return len(self.context.get("seg_labels_imgs"))
    
    def get_query_item(self, obj):
        return QueryItemSerializer(obj).data
    
    def get_options(self, obj):
        return [QueryOptionSerializer(t).data for t in self.context.get("seg_labels_imgs")]
