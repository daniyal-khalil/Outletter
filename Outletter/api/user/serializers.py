from rest_framework import serializers

from django.contrib.auth.password_validation import validate_password
from django.forms.fields import ImageField

from Outletter.user.models import User

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ("user_name", "email", "password", "confirm_password", "first_name", "last_name", "about", "profile_image")
    
    def validate(self, attrs):
        # This is validator for full attrs. Individual validators can also be made.
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create(
            user_name=validated_data['user_name'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            about=validated_data['about'],
            profile_image=validated_data['profile_image']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("about", "profile_image")
    
    def update(self, instance, validated_data):
        instance.about = validated_data.get('about', instance.about)
        instance.profile_image = validated_data.get('profile_image', instance.profile_image)
        instance.save()
        return instance

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("user_name", "email", "first_name", "last_name", "about", "profile_image")