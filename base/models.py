from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from django.conf import settings
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import datetime
from django.db.models import Q
from django.contrib.postgres.search import TrigramSimilarity
from django.contrib.postgres.indexes import GinIndex




def user_directory_path(instance , filename):
    return 'user_{0}/{}'.format(instance.user.id , filename)


class Category(models.Model):
    cid = ShortUUIDField(unique=True, length=10, max_length=30, prefix='cat', alphabet="abcdefghjkh12345")
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    imageUrl = models.URLField(max_length=200 , null=True, blank=True)
    
    def get_image_url(self):
        """Returns the image URL, prioritizing imageUrl if available."""
        if self.imageUrl:
            return self.imageUrl
        elif self.image:
            return self.image.url
        return None
    
    def category_image(self):
        """Returns an HTML img tag for the category image, handling both local and URL images."""
        if self.imageUrl:
            return mark_safe('<img src="%s" width="50" height="50" />' % (self.imageUrl))
        elif self.image:
            return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))
        return 'No Image'
                    
    @property
    def name(self):
        return self.title
        
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = "Categories"


class Brand(models.Model):
    bid = ShortUUIDField(unique=True, length=10, max_length=30, prefix='brd', alphabet="abcdefghjkh12345")
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="brands", null=True, blank=True)
    categories = models.ManyToManyField(Category, blank=True)
    
    class Meta:
        verbose_name_plural = "Brands"
        
    def brand_image(self):
        if self.image:
            return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))
        return 'No Image'
   
    def __str__(self):
        return self.title
    

class Tag(models.Model):
    DAILY_OFFER = "DailyOffer"
    RECENT = "Recent"
    BEST_SELLING_PRODUCT = "BestSelling"
    WEEKLY_PRODUCT = "Weekly"
    MONTHLY_PRODUCT = "Monthly"
    FLASH_PRODUCT = "Flash"
    SPECIAL_PRODUCT = "Special"

    TAG_CHOICES = [
        (DAILY_OFFER, "Daily Offer"),
        (RECENT, "Recent Product"),
        (BEST_SELLING_PRODUCT, "Best Selling Product"),
        (WEEKLY_PRODUCT, "Weekly Product"),
        (MONTHLY_PRODUCT, "Monthly Product"),
        (FLASH_PRODUCT, "Flash Product"),
        (SPECIAL_PRODUCT, "Special Product"),
    ]

    name = models.CharField(max_length=100, unique=True, choices=TAG_CHOICES)

    def __str__(self):
        return self.name


class Product(models.Model):
    pid = ShortUUIDField(unique=True, length=10, max_length=30, prefix='prd', alphabet="abcdefghjkh12345")
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, max_length=255)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="category")
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, related_name="products")
    image = models.ImageField(upload_to='products/', default="product.jpg")
    imageUrl = models.URLField(max_length=200, null=True, blank=True)
    In_stock = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, null=True)
    featured = models.BooleanField(default=False)
    product_status = models.CharField(max_length=200, default="published")
    tags = models.ManyToManyField(Tag, related_name='products', blank=True)
    
    
    def save(self, *args, **kwargs):
        if self.pk:  # Check if the product already exists in the database
            original = Product.objects.get(pk=self.pk)
            if original.title != self.title:  # Update slug only if the title has changed
                self.slug = slugify(self.title)
        else:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


    def product_image(self):
        """Returns the product image URL, prioritizing imageUrl if available."""
        image_src = self.imageUrl if self.imageUrl else self.image.url
        return mark_safe(f'<img src="{image_src}" width="50" height="50" />')

    def get_image_url(self):
        """Returns the actual image URL, giving preference to imageUrl."""
        return self.imageUrl if self.imageUrl else self.image.url

    @staticmethod
    def fuzzy_search(query):
        return Product.objects.annotate(
            similarity=TrigramSimilarity('title', query)
        ).filter(similarity__gt=0.3).order_by('-similarity')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Products"
        indexes = [
            GinIndex(
                fields=['title'],
                name='product_title_idx',
                opclasses=['gin_trgm_ops']
            ),
        ]


class ProductImages(models.Model):
    images = models.ImageField(upload_to="product-images", default="product.jpg")
    product = models.ForeignKey(Product, related_name="product_images", on_delete=models.SET_NULL, null=True) 
    date = models.DateTimeField(auto_now_add=True) 
    imageUrl = models.URLField(max_length=200 , null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Products Images"
        

class PromotionalBanner(models.Model):
    banner_title = models.CharField(max_length=200)
    banner_image_url = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.banner_title

    class Meta:
        verbose_name_plural = "Promotional Banners"
        ordering = ['-created_at']
        
