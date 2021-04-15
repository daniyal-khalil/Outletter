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

class LabelChoices(models.TextChoices):
    BRA = "Bra"
    BRIEFS = "Briefs"
    CAPRIS = "Capris"
    CASUALSHOES = "Casual Shoes"
    DRESSES = "Dresses"
    FLATS = "Flats"
    FLIPFLOPS = "Flip Flops"
    FORMALSHOES = "Formal Shoes"
    HEELS = "Heels"
    INNERVESTS = "Innerwear Vests"
    JACKETS = "Jackets"
    JEANS = "Jeans"
    KURTAS = "Kurtas"
    KURTIS = "Kurtis"
    LEGGINGS = "Leggings"
    NIGHTSUITS = "Night suits"
    NIGHTDRESS = "Nightdress"
    SANDALS = "Sandals"
    SAREES = "Sarees"
    SHIRTS = "Shirts"
    SHORTS = "Shorts"
    SKIRTS = "Skirts"
    SPORTSSHOES = "Sports Shoes"
    SWEATERS = "Sweaters"
    SWEATSHIRTS = "Sweatshirts"
    TOPS = "Tops"
    TRACKPANTS = "Track Pants"
    TROUSERS = "Trousers"
    TRUNK = "Trunk"
    TSHIRTS = "Tshirts"
    TUNICS = "Tunics"
    NONE = "None"