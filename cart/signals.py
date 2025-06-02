from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.contrib.auth.models import AnonymousUser
from .models import Cart as CartModel, CartItem
import logging

logger = logging.getLogger(__name__)

@receiver(user_logged_in)
def handle_user_login(sender, request, user, **kwargs):
    """
    Handle cart persistence when a user logs in.
    This will merge any session cart with the user's stored cart.
    """
    try:
        # Get the session cart
        session_cart = request.session.get('cart', {})
        
        # Get or create the user's database cart
        db_cart, created = CartModel.objects.get_or_create(user=user)
        
        # Get existing cart items
        existing_items = {str(item.product.id): item for item in CartItem.objects.filter(cart=db_cart)}
        
        # Process session cart items
        for product_id, data in session_cart.items():
            quantity = data.get('quantity', 0)
            
            if product_id in existing_items:
                # Update quantity if larger than existing
                existing_item = existing_items[product_id]
                if quantity > existing_item.quantity:
                    existing_item.quantity = quantity
                    existing_item.save()
            else:
                # Create new cart item
                CartItem.objects.create(
                    cart=db_cart,
                    product_id=product_id,
                    quantity=quantity
                )
        
        # Update session cart with merged data
        request.session['cart'] = {
            str(item.product.id): {'quantity': item.quantity}
            for item in CartItem.objects.filter(cart=db_cart)
        }
        request.session.modified = True
        
    except Exception as e:
        logger.error(f"Error handling cart during login: {e}")

@receiver(user_logged_out)
def handle_user_logout(sender, request, user, **kwargs):
    """
    Handle cart persistence when a user logs out.
    The cart is already saved in the database, so we just need to clear the session cart.
    """
    try:
        # Clear the session cart
        if 'cart' in request.session:
            del request.session['cart']
            request.session.modified = True
    except Exception as e:
        logger.error(f"Error handling cart during logout: {e}") 