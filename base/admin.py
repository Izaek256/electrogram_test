from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.admin.sites import site
from base.models import Product, Category, ProductImages, Brand, Tag, PromotionalBanner

admin.site.register(Tag)

class ProductImagesAdmin(admin.TabularInline):
    model = ProductImages
    
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImagesAdmin]
    list_display = ['title', 'price', 'category', 'brand', 'product_image', 'pid', 'display_tags']
    list_display_links = ['title', 'product_image']
    
    def display_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    
    display_tags.short_description = "Tags"


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'category_image', 'cid']  

# Register Category model with its admin class
admin.site.register(Category, CategoryAdmin)
    
class BrandAdmin(admin.ModelAdmin):
    list_display = ['title', 'image', 'get_categories']
    search_fields = ['title']
    
    def get_categories(self, obj):
        return ", ".join([category.title for category in obj.categories.all()])
    get_categories.short_description = 'Categories'
    
# Check if Brand is already registered
if not site.is_registered(Brand):
    admin.site.register(Brand, BrandAdmin)

admin.site.register(Product, ProductAdmin)

class UserAdmin(admin.ModelAdmin):
    model = User
    fields = ["username", "first_name", "last_name", "email"]
    
# Check if User is already registered before unregistering
if site.is_registered(User):
    admin.site.unregister(User)

admin.site.register(User, UserAdmin)

# Allow managing products under each Tag
class ProductInline(admin.TabularInline):  
    model = Product.tags.through  # ManyToManyField relation
    extra = 1  # Number of empty slots for adding products

class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "get_products")  # Display tag names and associated products
    inlines = [ProductInline]  # Show linked products inside each Tag
    
    def get_products(self, obj):
        return ", ".join([p.title for p in obj.products.all()])
    get_products.short_description = "Products"

admin.site.unregister(Tag)  # Unregister and re-register to apply changes
admin.site.register(Tag, TagAdmin)

class PromotionalBannerAdmin(admin.ModelAdmin):
    list_display = ['banner_title', 'banner_image_url', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['banner_title']
    readonly_fields = ['created_at', 'updated_at']

admin.site.register(PromotionalBanner, PromotionalBannerAdmin)


