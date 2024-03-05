# FROM: https://testdriven.io/blog/django-custom-user-model/
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=40, unique=True)
    password = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    organization = models.CharField(max_length=255)
    about = models.TextField(default=None, blank=True, null=True)
    picture = models.URLField(
        max_length=500, default=None, blank=True, null=True
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    list_autoreload = models.BooleanField(default=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.username
