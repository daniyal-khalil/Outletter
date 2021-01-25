from Outletter.item.models import ScrapedItem, QueryItem

from rest_framework import serializers

from src.choices import GenderChoices, ShopChoices

class QueryItemCreateSerializer(serializers.ModelSerializer):
    gender = serializers.ChoiceField(required=True, source='for_gender', choices=GenderChoices.choices)
    picture = serializers.ImageField(required=True)
    debug = serializers.BooleanField(required=True)
    shop = serializers.ChoiceField(required=True, choices=ShopChoices.choices)
    
    class Meta:
        model = QueryItem
        fields = ('picture', 'gender', 'shop', 'debug')

    def create(self, validated_data):
        print(validated_data)
        return QueryItem.objects.create(
            for_gender=validated_data['for_gender'],
            picture=validated_data['picture'],
            shop=validated_data['shop'],
            debug=validated_data['debug'],
        )


class QueryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryItem
        fields = '__all__'