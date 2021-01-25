from django.db import models

from Outletter.item.managers import QueryItemManager, ScrapedItemManager

from src.choices import GenderChoices, ShopChoices

class BaseItem(models.Model):
    picture = models.ImageField(upload_to='item_pictures')
    for_gender = models.CharField(choices=GenderChoices.choices, max_length=6, default=GenderChoices.MALE)
    shop = models.CharField(choices=ShopChoices.choices, max_length=256, default=ShopChoices.KOTON)

    REQUIRED_FIELDS = ['picture', 'for_gender', 'shop']

    class Meta:
        verbose_name = "Base Item"
        abstract = True

    def __str__(self):
        return self.id

class ScrapedItem(BaseItem):
    name = models.CharField(max_length=128, blank=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    url = models.CharField(max_length=256)

    objects = ScrapedItemManager()
    REQUIRED_FIELDS = ['price', 'url']

    class Meta:
        verbose_name = "Scraped Item"

    def __str__(self):
        return self.name

class QueryItem(BaseItem):
    debug = models.BooleanField(default=False)

    objects = QueryItemManager()
    REQUIRED_FIELDS = ['debug',]

    class Meta:
        verbose_name = "Query Item"

    def __str__(self):
        return self.id
