from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    email = models.EmailField(max_length=200, unique=True)
    phone_number = models.CharField(max_length=20)
    user_type = models.BooleanField(default=True)
    address = models.CharField(max_length=255)
    username = models.CharField(max_length=30, unique=False)
    
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]


    def __str__(self):
        return self.username

    class Meta:
        db_table = 'user'