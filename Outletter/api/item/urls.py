from django.urls import path
from Outletter.api.item.views import ItemListView, ItemListTestView, ItemView, ItemInfoView

app_name = "item_api"

urlpatterns = [
    path("items/", ItemListView.as_view(), name="similar-items"),
    path("items/info/", ItemInfoView.as_view(), name="info-items"),
    path("item/<int:id>/", ItemView.as_view({"get": "retrieve"}), name="item"),
    path("test/", ItemListTestView.as_view(), name="testing"),
]
