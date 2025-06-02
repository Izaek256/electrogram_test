from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from base.models import Product
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.core.validators import RegexValidator

# Create your models here.

class DeliveryAddress(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    delivery_full_name = models.CharField(max_length=255)
    delivery_email = models.EmailField(max_length=255, default="default@gmail.com")
    delivery_address = models.CharField(max_length=255)
    delivery_phone_number = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+256\d{9}$',
                message='Phone number must be in the format: +256XXXXXXXXX'
            )
        ],
        help_text='Enter phone number with country code (e.g., +256XXXXXXXXX)'
    )
    delivery_city = models.CharField(max_length=255, null=True, blank=True)
    delivery_district = models.CharField(max_length=255, null=True, blank=True)
    details_about_address = models.TextField(null=True, blank=True)
    
    class Meta:
        verbose_name_plural = 'DeliveryAddress'
        
    def __str__(self):
        return f'Delivery Address - {str(self.id) if self.id else "None"}'

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, default="default@gmail.com")
    amount_paid = models.DecimalField(max_digits=20, decimal_places=2, default="0.00")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Order Creation Date")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Update")
    invoice_number = models.CharField(max_length=50, unique=True, blank=True, null=True, editable=False)
    invoice_date = models.DateField(default=timezone.now)
    due_date = models.DateField(blank=True, null=True)
    company_info = models.TextField(default="Electrogram LLC\nellectrogramllc.com\nTel: (+256 752235731)\nHome Of Electronics")

    class Meta:
        verbose_name_plural = "Orders"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            super().save(*args, **kwargs)
            self.invoice_number = f"INV-{self.user.id}-{self.id:06d}"

            super().save(update_fields=['invoice_number'])
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"Order: {self.id}"
        
    def order_date(self):
        return self.created_at.strftime('%B %d, %Y')

class OrderItems(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name_plural = "Order Items"
        unique_together = ('order', 'product')

    def order_img(self):
        if self.product.image:
            return mark_safe('<img src="%s" width="50" height="50"/>' % (self.product.image.url))
        return 'No Image'

    def __str__(self):
        return f"{self.product.title} (x{self.quantity}) - Total: ${self.price} "
