from django.urls import path
from Outletter.api.like.views import MyLikes

app_name = "like_api"

urlpatterns = [
    path("like/", MyLikes.as_view({"post": "create",
                                        "get": "list"}), name="like-list"),
    path("like/<int:id>/", MyLikes.as_view({"get": "retrieve",
                                                "delete": "destroy"}), name="like-detail"),
]