from Outletter.review.models import Review
from rest_framework import serializers

class ReviewCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    content = serializers.CharField(required=True)
    
    class Meta:
        model = Review
        fields = ('title', 'content', 'rel_item')

    def create(self, validated_data):
        return Review.objects.create(
            title=validated_data['title'],
            content=validated_data['content'],
            rel_item=validated_data['rel_item'],
            rel_user=self.context.get("request").user,
        )

class ReviewUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    content = serializers.CharField(required=True)

    class Meta:
        model = Review
        fields = ('title', 'content')

class ReviewDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"