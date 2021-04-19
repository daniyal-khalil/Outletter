from django.contrib import admin

from Outletter.review.models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id",)