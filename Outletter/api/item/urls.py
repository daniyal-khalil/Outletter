from django.urls import path
from Outletter.api.item.views import ItemListView

app_name = "item_api"

urlpatterns = [
    path("items/", ItemListView.as_view(), name="similar-items"),
]