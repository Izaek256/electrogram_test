from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import Profile

User = get_user_model()


# Register the User model
admin.site.register(User, UserAdmin)# Register the User model
admin.site.register(Profile)