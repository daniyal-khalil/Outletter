from django.contrib import admin
from django.core.paginator import Paginator

from Outletter.item.models import QueryItem

@admin.register(QueryItem)
class QueryItemAdmin(admin.ModelAdmin):
    list_display = ("picture",)
    # search_fields = ("name", "price", "url", "picture")
    # paginator = Paginator
    # list_per_page = 5
    # fieldsets = (
    #     (None,  {
    #         "fields": ("name",)
    #     }),
    #     ("Shopping Detail", {
    #         "fields": ("price", "url", "picture")
    #     })
    # )