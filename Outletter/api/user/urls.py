from django.urls import path
from Outletter.api.user.views import RegisterUser, UserDetail

from rest_framework.authtoken.views import obtain_auth_token

app_name = "user_api"

urlpatterns = [
    path("user/register/", RegisterUser.as_view({"post": "create"}), name="user-create"),
    path("user/me/", UserDetail.as_view({"get": "retrieve", "patch": "partial_update"}), name="user-detail"),
    path("user/login/", obtain_auth_token, name="user-login"),
]