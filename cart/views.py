from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .cart import Cart
from base.models import Product
import logging
from django.contrib import messages

logger = logging.getLogger(__name__)

def cart_summary(request):
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()
    return render(request, "cart/cart.html", {"cart_products": cart_products, "quantities": quantities, "total": totals})






def cart_add(request, product_id):
    cart = Cart(request)
    
    if request.method == 'POST' and request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty', 1))
        
        # Ensure the product exists
        product = get_object_or_404(Product, id=product_id)
        
        if product_id in cart.get_quants():
            messages.info(request, 'This item is already in your cart. You can update the quantity in your cart.')
            return JsonResponse({'qty': len(cart), 'message': 'Product is already in the cart.'})
        else:
            cart.add(product=product, quantity=product_qty)

        cart_quantity = len(cart)
        
        response = JsonResponse({'qty': cart_quantity, 'message': 'Product added to cart successfully'})
        messages.success(request, f'"{product.title}" has been added to your cart.')
        return response
    
    return JsonResponse({'error': 'Invalid request'}, status=400)






def cart_delete(request):
    cart = Cart(request)
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        
        cart.delete(product=product_id)
        
        response = JsonResponse({
            'product': product_id,
            'status': 'success',
            'message': 'Item has been removed from your cart.'
        })
        messages.success(request, 'Item has been removed from your cart.')
        return response



def cart_update(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product_qty = request.POST.get('product_qty')

        logger.debug(f"Received product_id: {product_id}, product_qty: {product_qty}")

        if product_qty == '':
            messages.error(request, 'Please enter a valid quantity.')
            return JsonResponse({'error': 'Product quantity cannot be empty.'}, status=400)

        try:
            product_qty = int(product_qty)
        except ValueError:
            messages.error(request, 'Please enter a valid number for quantity.')
            return JsonResponse({'error': 'Invalid quantity.'}, status=400)

        cart = Cart(request)

        # Check if the product exists in the cart
        cart_products = cart.get_prods()  # Get the list of products in the cart
        if str(product_id) not in [str(product.id) for product in cart_products]:  # Ensure product_id is a string
            logger.debug(f"Product ID {product_id} not found in cart products: {[product.id for product in cart_products]}")
            messages.error(request, 'This item is no longer in your cart.')
            return JsonResponse({'error': 'Product not found in cart.'}, status=400)

        cart.update(product=product_id, quantity=product_qty)
        messages.success(request, 'Cart quantity has been updated successfully.')
        response = JsonResponse({'qty': product_qty, 'message': 'Product quantity updated successfully'})
        return response
