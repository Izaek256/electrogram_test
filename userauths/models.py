from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

class User(AbstractUser):
    email = models.EmailField(unique=True, null=False, blank=False)
    username = models.CharField(max_length=200, unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.username} ({self.email})"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    username = models.CharField(max_length=200, unique=True, default='default_username')
    email = models.EmailField(unique=True, null=False, blank=False, default='default@example.com')
    first_name = models.CharField(max_length=30, blank=True, default='default_first_name')
    last_name = models.CharField(max_length=30, blank=True, default='default_last_name')
    
    def __str__(self):
        return self.user.username





