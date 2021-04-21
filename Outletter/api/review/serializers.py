from Outletter.review.models import Review
from rest_framework import serializers
from Outletter.item.models import ScrapedItem

class ReviewCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True, max_length=255)
    content = serializers.CharField(required=True, max_length=500)
    rating = serializers.DecimalField(required=True, max_digits=2, decimal_places=1)
    
    class Meta:
        model = Review
        fields = ('title', 'content', 'rel_item', 'rating')

    def create(self, validated_data):
        return Review.objects.create(
            title=validated_data['title'],
            content=validated_data['content'],
            rel_item=validated_data['rel_item'],
            rating=validated_data['rating'],
            rel_user=self.context.get("request").user,
        )

class ReviewUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True, max_length=255)
    content = serializers.CharField(required=True, max_length=500)
    rating = serializers.DecimalField(required=True, max_digits=2, decimal_places=1)

    class Meta:
        model = Review
        fields = ('title', 'content', 'rating')

class ScrapedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapedItem
        fields = '__all__'

    def to_representation(self, instance):
        result = super(ScrapedItemSerializer, self).to_representation(instance)
        if not self.context.get("debug", None):
            result.pop("label")
        return result

class ReviewDetailSerializer(serializers.ModelSerializer):
    rel_item = serializers.SerializerMethodField()

    def get_rel_item(self, obj):
        return ScrapedItemSerializer(obj.rel_item).data

    class Meta:
        model = Review
        fields = ('id', 'title', 'content', 'rating', 'rel_user', 'rel_item')