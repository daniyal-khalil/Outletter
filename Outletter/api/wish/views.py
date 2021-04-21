from rest_framework import permissions, status, response

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, CreateModelMixin, UpdateModelMixin, ListModelMixin, DestroyModelMixin

from Outletter.api.wish.serializers import WishCreateSerializer, WishDetailSerializer
from Outletter.wish.models import Wish

class MyWishes(CreateModelMixin, UpdateModelMixin, RetrieveModelMixin, ListModelMixin, DestroyModelMixin, GenericViewSet):
	queryset = Wish.objects.all()
	permission_classes = (permissions.IsAuthenticated,)
	lookup_field = "id"
	lookup_url_kwarg = "id"

	def get_queryset(self):
		return self.queryset.filter(rel_user=self.request.user)
	
	def get_serializer_class(self):
		if self.action == "create":
			return WishCreateSerializer
		else:
			return WishDetailSerializer