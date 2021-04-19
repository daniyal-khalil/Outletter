from django.db import models
from django.utils.translation import gettext_lazy as _

class Review(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(max_length=500)
    rel_user = models.ForeignKey(
        verbose_name=_("User Review"),
        to="user.User",
        on_delete=models.CASCADE,
        related_name="user_reviews",
        related_query_name="user_reviews",
    )
    rel_item = models.ForeignKey(
        verbose_name=_("Item Review"),
        to="item.ScrapedItem",
        on_delete=models.CASCADE,
        related_name="user_reviews",
        related_query_name="user_reviews",
    )
    # Date & Time
    created_at = models.DateTimeField(verbose_name=_("Added"), auto_now_add=True)
    modified_at = models.DateTimeField(verbose_name=_("Last modified"), auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Review"

    def __str__(self):
        return self.id

    