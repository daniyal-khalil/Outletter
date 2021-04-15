from django.db import models
from django.utils.translation import gettext_lazy as _

class QueryItemManager(models.Manager):
    def create_queryitem(self, debug, picture, for_gender, shop, **other_fields):
        return self.model(debug=debug, picture=picture, for_gender=for_gender, shop=shop, **other_fields)

class ScrapedItemManager(models.Manager):
    def create_scrapeditem(self, name, price, url, picture, for_gender, shop, **other_fields):
        return self.model(name=name, picture=picture, for_gender=for_gender, shop=shop,
                            price=price, url=url, **other_fields)