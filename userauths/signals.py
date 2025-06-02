from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to create or update user profile.
    Ensures only one profile exists per user.
    """
    if created:
        Profile.objects.create(user=instance)
    else:
        # Update existing profile or create if it doesn't exist
        profile, created = Profile.objects.get_or_create(user=instance)
        # Update profile fields with user data
        profile.username = instance.username
        profile.email = instance.email
        profile.first_name = instance.first_name
        profile.last_name = instance.last_name
        profile.save()
