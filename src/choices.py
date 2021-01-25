from django.db import models
from django.utils.translation import gettext_lazy as _

class GenderChoices(models.TextChoices):
    MALE = "male", _("Male")
    FEMALE = "female", _("Female")
    
class ShopChoices(models.TextChoices):
    KOTON = "www.koton.com"
    LCWAIKIKI = "www.lcwaikiki.com"
    BOYNER = "www.boyner.com.tr"
    DEFACTO = "www.defacto.com.tr"
    TRENDYOL = "www.trendyol.com"
    HM = "www2.hm.com/tr_tr"