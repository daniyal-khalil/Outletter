from rest_framework import permissions, status, response

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, CreateModelMixin, UpdateModelMixin, ListModelMixin, DestroyModelMixin

from Outletter.api.review.serializers import ReviewCreateSerializer, ReviewUpdateSerializer, ReviewDetailSerializer
from Outletter.review.models import Review

class MyReviews(CreateModelMixin, UpdateModelMixin, RetrieveModelMixin, ListModelMixin, DestroyModelMixin, GenericViewSet):
	queryset = Review.objects.all()
	permission_classes = (permissions.IsAuthenticated,)
	lookup_field = "id"
	lookup_url_kwarg = "id"

	def get_queryset(self):
		return self.queryset.filter(rel_user=self.request.user)
	
	def get_serializer_class(self):
		if self.action == "partial_update":
			return ReviewUpdateSerializer
		elif self.action == "create":
			return ReviewCreateSerializer
		else:
			return ReviewDetailSerializer