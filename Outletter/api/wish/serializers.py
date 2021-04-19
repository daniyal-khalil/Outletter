from Outletter.wish.models import Wish
from rest_framework import serializers

class WishCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wish
        fields = ('rel_item', )

    def create(self, validated_data):
        return Wish.objects.create(
            rel_item=validated_data['rel_item'],
            rel_user=self.context.get("request").user,
        )

class WishDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wish
        fields = "__all__"