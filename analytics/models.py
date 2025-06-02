from django.db import models
from django.utils.timezone import now
from django.conf import settings

class UserActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='user_activities')
    page_url = models.CharField(max_length=500)
    click_x = models.IntegerField(null=True, blank=True)
    click_y = models.IntegerField(null=True, blank=True)
    time_spent = models.FloatField(default=0)  # Time in seconds
    timestamp = models.DateTimeField(default=now)

class Product(models.Model):
    name = models.CharField(max_length=255)
    views = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    search_count = models.IntegerField(default=0)

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='analytics_carts')
    checked_out = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='analytics_orders')
    created_at = models.DateTimeField(auto_now_add=True)

class ProductInteraction(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='product_interactions')
    views = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    added_to_cart = models.IntegerField(default=0)
    purchased = models.IntegerField(default=0)

