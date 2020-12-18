from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=128)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    url = models.CharField(max_length=256)
    picture = models.CharField(max_length=256)

    class Meta:
        verbose_name = "Item"

    def __str__(self):
        return self.name
