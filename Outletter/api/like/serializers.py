from Outletter.like.models import Like
from rest_framework import serializers

class LikeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ('rel_item', )

    def create(self, validated_data):
        return Like.objects.create(
            rel_item=validated_data['rel_item'],
            rel_user=self.context.get("request").user,
        )

class LikeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = "__all__"