from django.db import models
from django.contrib.auth.models import AbstractUser

from .managers import UserManager


class User(AbstractUser):
    username = models.CharField(max_length=100, unique=True, null=False, blank=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    bio = models.CharField(max_length=20, null=True, blank=True, default="")
    image = models.ImageField(upload_to="images/users/", null=True, blank=True)
    activity = models.IntegerField(null=True, blank=True, default=0)
    is_student = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = "username"

    def __str__(self):
        return self.username
