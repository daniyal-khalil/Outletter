from django.urls import path
from Outletter.api.review.views import MyReviews

app_name = "review_api"

urlpatterns = [
    path("review/", MyReviews.as_view({"post": "create",
                                        "get": "list"}), name="review-list"),
    path("review/<int:id>/", MyReviews.as_view({"get": "retrieve",
                                                "patch": "partial_update",
                                                "delete": "destroy"}), name="review-detail"),
]