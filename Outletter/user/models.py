from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from Outletter.user.managers import UserManager

from src.choices import GenderChoices

class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    email = models.EmailField(_('email address'), unique=True)
    user_name = models.CharField(max_length=128, unique=True)
    about = models.TextField(_('about'), max_length=500, blank=True)
    gender = models.CharField(choices=GenderChoices.choices, max_length=6, null=True, blank=True,)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    profile_image = models.ImageField(upload_to='profile_pictures', null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_name', 'first_name', 'last_name']

    class Meta:
        verbose_name = "User"

    def __str__(self):
        return self.first_name + " " + self.last_name

