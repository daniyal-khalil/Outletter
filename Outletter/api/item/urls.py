from django.urls import path
from Outletter.api.item.views import ItemListView, CustomerImageUploadView

app_name = "item_api"

urlpatterns = [
    path("Items/", ItemListView.as_view(), name="Items"),
    path("similarItems/", CustomerImageUploadView.as_view(), name="similarItems")
]