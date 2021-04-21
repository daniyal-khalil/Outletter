from django.db import models
from django.utils.translation import gettext_lazy as _

class Like(models.Model):
    rel_user = models.ForeignKey(
        verbose_name=_("User Like"),
        to="user.User",
        on_delete=models.CASCADE,
        related_name="user_likes",
        related_query_name="user_likes",
    )
    rel_item = models.ForeignKey(
        verbose_name=_("Item Like"),
        to="item.ScrapedItem",
        on_delete=models.CASCADE,
        related_name="user_likes",
        related_query_name="user_likes",
    )
    # Date & Time
    created_at = models.DateTimeField(verbose_name=_("Added"), auto_now_add=True)
    modified_at = models.DateTimeField(verbose_name=_("Last modified"), auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Like"

    def __str__(self):
        return self.id

    