from django.urls import path
from Outletter.api.wish.views import MyWishes

app_name = "wish_api"

urlpatterns = [
    path("wish/", MyWishes.as_view({"post": "create",
                                        "get": "list"}), name="wish-list"),
    path("wish/<int:id>/", MyWishes.as_view({"get": "retrieve",
                                                "delete": "destroy"}), name="wish-detail"),
]