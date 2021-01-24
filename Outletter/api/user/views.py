from rest_framework import permissions, status, response

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, CreateModelMixin, UpdateModelMixin

from Outletter.api.user.serializers import UserCreateSerializer, UserUpdateSerializer, UserDetailSerializer
from Outletter.user.models import User

class RegisterUser(CreateModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = (permissions.AllowAny,)
    # you can override create method

class UserDetail(UpdateModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def retrieve(self, request, *args, **kwargs):
        return response.Response(UserDetailSerializer(request.user).data, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        userSerializer = UserUpdateSerializer(request.user, data=request.data)
        if userSerializer.is_valid():
            userSerializer.save()
            return response.Response(UserDetailSerializer(request.user).data, status=status.HTTP_200_OK)
        else:
            return response.Response(userSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_class(self):
        if self.action == "partial_update":
            return UserUpdateSerializer
        else:
            return UserDetailSerializer