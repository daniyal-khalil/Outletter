from django.contrib import admin

from Outletter.wish.models import Wish

@admin.register(Wish)
class WishAdmin(admin.ModelAdmin):
    list_display = ("id",)