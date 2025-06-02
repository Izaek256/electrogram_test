from base.models import Product
from django.shortcuts import get_object_or_404
import logging
from .models import Cart as CartModel, CartItem
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)

class Cart():
    def __init__(self, request):
        self.session = request.session
        self.user = request.user if not isinstance(request.user, AnonymousUser) else None
        
        # Current session key
        cart = self.session.get("cart")
        
        # New user create one
        if 'cart' not in request.session:
            cart = self.session['cart'] = {}
        
        # Availability
        self.cart = cart
        
        # If user is authenticated, load their cart from database
        if self.user:
            self._load_db_cart()
    
    def _load_db_cart(self):
        """Load cart from database for authenticated users"""
        try:
            db_cart, created = CartModel.objects.get_or_create(user=self.user)
            cart_items = CartItem.objects.filter(cart=db_cart)
            
            # Merge database cart with session cart
            for item in cart_items:
                product_id = str(item.product.id)
                if product_id not in self.cart:
                    self.cart[product_id] = {'quantity': item.quantity}
                else:
                    # If item exists in both, use the larger quantity
                    self.cart[product_id]['quantity'] = max(
                        self.cart[product_id]['quantity'],
                        item.quantity
                    )
            
            self.save()
        except Exception as e:
            logger.error(f"Error loading database cart: {e}")
    
    def _save_to_db(self):
        """Save cart to database for authenticated users"""
        if not self.user:
            return
            
        try:
            db_cart, created = CartModel.objects.get_or_create(user=self.user)
            
            # Clear existing items
            CartItem.objects.filter(cart=db_cart).delete()
            
            # Save new items
            for product_id, data in self.cart.items():
                product = get_object_or_404(Product, id=product_id)
                CartItem.objects.create(
                    cart=db_cart,
                    product=product,
                    quantity=data['quantity']
                )
        except Exception as e:
            logger.error(f"Error saving to database cart: {e}")
    
    def add(self, product, quantity=1):
        product_id = str(product.id)
        
        # Check if the product is already in the cart
        if product_id in self.cart:
            logger.info(f"Product {product_id} is already in the cart. No quantity update.")
            return  # Do not update quantity if already in cart
        
        self.cart[product_id] = {'quantity': 0}  # Initialize as a dictionary
        
        # Update the quantity based on the input
        self.cart[product_id]['quantity'] += quantity  # Increment the existing quantity
        self.save()
        
    def save(self):
        self.session.modified = True
        if self.user:
            self._save_to_db()
        
    def __len__(self):
        # Return the number of unique products in the cart
        return len(self.cart)
    
    def get_prods(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        return products
    
    def get_quants(self):
        quantities = self.cart
        return quantities
    
    def cart_total(self):
        total = 0
        logger.debug(f"Current cart structure: {self.cart}")  # Log the current structure of the cart
        for product_id, value in self.cart.items():  # Assuming self.cart is a dictionary
            logger.debug(f"Processing product_id: {product_id}, value: {value}")  # Log each product's value
            product = get_object_or_404(Product, id=product_id)
            # Ensure value is a dictionary and has the 'quantity' key
            if isinstance(value, dict) and 'quantity' in value:
                total += product.price * value['quantity']
            else:
                logger.error(f"Unexpected value format for product_id {product_id}: {value}")
                # Handle the case where value is not as expected
        return total
    
    def update(self, product, quantity):
        product_id = str(product)
        product_qty = int(quantity)
        
        # Ensure the product exists in the cart
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0}  # Initialize if not present

        # Update the quantity
        self.cart[product_id]['quantity'] = product_qty  # Set the quantity directly

        self.session.modified = True
        if self.user:
            self._save_to_db()
            
        result = self.cart
        return result
    
    def delete(self, product):
        product_id = str(product)
        
        if product_id in self.cart:
            del self.cart[product_id]
        
        self.session.modified = True
        if self.user:
            self._save_to_db()
            
    def clear(self):
        """Clear all items from the cart (session and DB if authenticated)"""
        self.cart.clear()
        self.session['cart'] = self.cart
        self.session.modified = True
        if self.user:
            try:
                db_cart, created = CartModel.objects.get_or_create(user=self.user)
                CartItem.objects.filter(cart=db_cart).delete()
            except Exception as e:
                logger.error(f"Error clearing database cart: {e}")
