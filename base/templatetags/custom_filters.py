from django import template
from base.models import Product

register = template.Library()

@register.filter
def get_item_image(order_id):
    try:
        # Assuming there is a way to get the product associated with the order
        product = Product.objects.get(id=order_id)
        return product.image.url if product.image else None
    except Product.DoesNotExist:
        return None
