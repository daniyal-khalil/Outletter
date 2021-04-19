from django.contrib import admin

from Outletter.like.models import Like

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id",)