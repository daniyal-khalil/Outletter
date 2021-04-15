from django.urls import path
from Outletter.api.user.views import RegisterUser, UserDetail

app_name = "user_api"

urlpatterns = [
    path("reg-user/", RegisterUser.as_view({"post": "create"}), name="user-create"),
    path("user/", UserDetail.as_view({"get": "retrieve", "patch": "partial_update"}), name="user-detail"),
]