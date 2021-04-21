from rest_framework import permissions, status, response

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, CreateModelMixin, UpdateModelMixin, ListModelMixin, DestroyModelMixin

from Outletter.api.like.serializers import LikeCreateSerializer, LikeDetailSerializer
from Outletter.like.models import Like

class MyLikes(CreateModelMixin, RetrieveModelMixin, ListModelMixin, DestroyModelMixin, GenericViewSet):
	queryset = Like.objects.all()
	permission_classes = (permissions.IsAuthenticated,)
	lookup_field = "id"
	lookup_url_kwarg = "id"

	def get_queryset(self):
		return self.queryset.filter(rel_user=self.request.user)
	
	def get_serializer_class(self):
		if self.action == "create":
			return LikeCreateSerializer
		else:
			return LikeDetailSerializer