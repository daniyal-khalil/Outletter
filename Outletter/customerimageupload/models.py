from django.db import models 

genderChoice = (('m','male'), ('f','female'))

class CustomerImageUpload(models.Model):
    image = models.ImageField("QueryImages") 
    debug = models.BooleanField()
    shop = models.IntegerField()
    gender = models.CharField(max_length=1, choices=genderChoice)

