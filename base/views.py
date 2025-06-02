from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.db import models
from base.models import Product, Category, ProductImages, Brand, Tag
from django.core.paginator import Paginator
from django.db.models import Count, Q, Value, FloatField
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import login, authenticate
from django.conf import settings
from .forms import UserInfoForm
from django import forms
from payments.forms import DeliveryAddressForm
from payments.models import DeliveryAddress, Order
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from payments.models import Order, OrderItems
from django.template.loader import render_to_string
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.postgres.search import TrigramSimilarity, SearchVector, SearchQuery, SearchRank
from django.db.models.functions import Greatest



def index(request):
    # Handle HTMX requests for different sections
    if request.headers.get('HX-Request'):
        section = request.GET.get('section')
        page = request.GET.get('page', 1)
        
        if section == 'daily-offer':
            products = Product.objects.filter(tags__name=Tag.DAILY_OFFER).order_by('-date')
            paginator = Paginator(products, 2)
            products_page = paginator.get_page(page)
            return render(request, 'core/partials/daily_offer_products.html', {
                'products': products_page
            })
        elif section == 'recent-products':
            products = Product.objects.filter(tags__name=Tag.RECENT).order_by('-date', '-id')
            paginator = Paginator(products, 4)
            products_page = paginator.get_page(page)
            return render(request, 'core/partials/recent_products.html', {
                'products': products_page
            })
        elif section == 'best-selling':
            products = Product.objects.filter(tags__name=Tag.BEST_SELLING_PRODUCT).order_by('-date', '-id')
            paginator = Paginator(products, 4)
            products_page = paginator.get_page(page)
            return render(request, 'core/partials/best_selling_products.html', {
                'products': products_page
            })
        elif section == 'monthly-products':
            products = Product.objects.filter(tags__name=Tag.MONTHLY_PRODUCT).order_by('-date', '-id')
            paginator = Paginator(products, 4)
            products_page = paginator.get_page(page)
            return render(request, 'core/partials/monthly_products.html', {
                'products': products_page
            })

    # Regular page load - get all data
    products = Product.objects.all()
    categories = Category.objects.all().order_by('id')
    
    # Get daily offer products and paginate
    daily_offer_products_list = Product.objects.filter(tags__name=Tag.DAILY_OFFER).order_by('-date')
    paginator = Paginator(daily_offer_products_list, 2)
    page = request.GET.get('page')
    daily_offer_products = paginator.get_page(page)
    
    # Get and paginate recent products
    recent_products_list = Product.objects.filter(tags__name=Tag.RECENT).order_by('-date', '-id')
    recent_paginator = Paginator(recent_products_list, 4)
    recent_page = request.GET.get('recent_page')
    recent_products = recent_paginator.get_page(recent_page)
    
    # Get and paginate best selling products
    best_selling_products_list = Product.objects.filter(tags__name=Tag.BEST_SELLING_PRODUCT).order_by('-date', '-id')
    best_selling_paginator = Paginator(best_selling_products_list, 4)
    best_selling_page = request.GET.get('best_selling_page')
    best_selling_products = best_selling_paginator.get_page(best_selling_page)
    
    weekly_products = Product.objects.filter(tags__name=Tag.WEEKLY_PRODUCT).order_by('-date', '-id')
    monthly_products = Product.objects.filter(tags__name=Tag.MONTHLY_PRODUCT).order_by('-date', '-id')
    flash_products = Product.objects.filter(tags__name=Tag.FLASH_PRODUCT).order_by('-date', '-id')
    special_products = Product.objects.filter(tags__name=Tag.SPECIAL_PRODUCT).order_by('-date', '-id')
    
    # Get all active brands
    brands = Brand.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'daily_offer_products': daily_offer_products,
        'recent_products': recent_products,
        'best_selling_products': best_selling_products,
        'weekly_products': weekly_products,
        'monthly_products': monthly_products,
        'flash_products': flash_products,
        'special_products': special_products,
        'brands': brands  # Add brands to the context
    }
    return render(request, 'core/index.html', context)

def category_list_view(request):
    # Initialize base queryset with product count
    category_list = Category.objects.annotate(
        product_count=Count('category')
    ).order_by('id')

    # Pagination
    paginator = Paginator(category_list, 8)  # Show 12 categories per page
    page = request.GET.get('page', 1)
    categories_paginated = paginator.get_page(page)

    context = {
        'categories': categories_paginated,
    }
    
    # Check if this is an HTMX request
    if request.headers.get('HX-Request'):
        return render(request, 'core/partials/category_products.html', context)
    
    # Normal request - render the full template
    return render(request, 'core/category-list.html', context)

def product_category_list_view(request, cid):
    category = get_object_or_404(Category, cid=cid)
    
    # Get all products for this category
    products_list = Product.objects.filter(category=category).order_by('-date')
    
    # Apply filters if present
    brand_ids = request.GET.getlist('brand')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    
    if brand_ids:
        products_list = products_list.filter(brand__id__in=brand_ids)
    if price_min:
        products_list = products_list.filter(price__gte=price_min)
    if price_max:
        products_list = products_list.filter(price__lte=price_max)
    
    total_products = products_list.count()
    
    # Set up pagination
    paginator = Paginator(products_list, 8)  # Show 8 products per page
    page = request.GET.get('page', 1)
    products = paginator.get_page(page)
    
    # Get all brands that have products in this category
    brands = Brand.objects.filter(products__category=category).distinct()
    
    # Get min and max prices for this category
    price_range = products_list.aggregate(min_price=models.Min('price'), max_price=models.Max('price'))
    
    # Handle HTMX requests for filtered results
    if request.headers.get('HX-Request') and 'filter' in request.GET:
        return render(request, 'core/partials/product_card_list.html', {
            'products': products,
            'category': category,
        })
    
    # Handle HTMX requests for pagination
    elif request.headers.get('HX-Request'):
        return render(request, 'core/partials/product_card_list.html', {
            'products': products,
            'category': category,
        })
    
    # For initial page load, render the full template
    context = {
        "category": category,
        "products": products,
        "total_products": total_products,
        "brands": brands,
        "price_range": price_range,
        "selected_brands": [int(bid) for bid in brand_ids] if brand_ids else [],
        "price_min": price_min or price_range.get('min_price', 0),
        "price_max": price_max or price_range.get('max_price', 1000000),
    }
    return render(request, "core/category-product-list.html", context)

def product_detail_view(request, slug):
    product = get_object_or_404(Product, slug=slug)
    # Get related products from same category, excluding current product
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(
        id=product.id
    ).order_by('-date')[:8]  # Limit to 8 related products
    
    p_images = product.product_images.all()

    context = {
        "p": product,
        "p_image": p_images,
        "products": related_products,  # Pass related products to template
    }
    return render(request, "core/product-detail.html", context)

def search_view(request):
    query = request.GET.get("q", "").strip()
    
    if not query:
        return render(request, "core/search.html", {
            "products": [],
            "query": "",
            "related_products": []
        })
    
    # Initialize lists for different types of matches
    exact_title_matches = list(Product.objects.filter(title__iexact=query))
    fuzzy_title_matches = list(Product.objects.annotate(
        similarity=TrigramSimilarity('title', query)
    ).filter(
        similarity__gt=0.3
    ).exclude(
        id__in=[p.id for p in exact_title_matches]
    ).order_by('-similarity'))
    
    category_matches = list(Product.objects.filter(
        category__title__icontains=query
    ).exclude(
        id__in=[p.id for p in exact_title_matches] + [p.id for p in fuzzy_title_matches]
    ))
    
    brand_matches = list(Product.objects.filter(
        brand__title__icontains=query
    ).exclude(
        id__in=[p.id for p in exact_title_matches] + [p.id for p in fuzzy_title_matches] + [p.id for p in category_matches]
    ))
    
    description_matches = list(Product.objects.filter(
        description__icontains=query
    ).exclude(
        id__in=[p.id for p in exact_title_matches] + [p.id for p in fuzzy_title_matches] + 
               [p.id for p in category_matches] + [p.id for p in brand_matches]
    ))
    
    # Combine all matches in priority order
    products_list = (exact_title_matches + fuzzy_title_matches + 
                    category_matches + brand_matches + description_matches)
    
    # Get related products based on the type of match found
    related_products = []
    if products_list:
        first_match = products_list[0]
        
        # If we have exact or fuzzy title matches, get related products by title similarity
        if exact_title_matches or fuzzy_title_matches:
            # Get products with similar titles
            title_similar = Product.objects.annotate(
                similarity=TrigramSimilarity('title', query)
            ).filter(
                similarity__gt=0.2
            ).exclude(
                id__in=[p.id for p in products_list]
            ).order_by('-similarity', '-date')
            
            # Get products from the same category
            category_similar = Product.objects.filter(
                category=first_match.category
            ).exclude(
                id__in=[p.id for p in products_list] + [p.id for p in title_similar]
            ).order_by('-date')
            
            # Get products from the same brand
            brand_similar = Product.objects.filter(
                brand=first_match.brand
            ).exclude(
                id__in=[p.id for p in products_list] + [p.id for p in title_similar] + [p.id for p in category_similar]
            ).order_by('-date')
            
            # Combine all related products
            related_products = list(title_similar) + list(category_similar) + list(brand_similar)
        
        # If we have category matches, get related products from the same category and similar categories
        elif category_matches:
            # Get products from the same category
            same_category = Product.objects.filter(
                category=first_match.category
            ).exclude(
                id__in=[p.id for p in products_list]
            ).order_by('-date')
            
            # Get products from similar categories
            similar_categories = Product.objects.annotate(
                similarity=TrigramSimilarity('category__title', first_match.category.title)
            ).filter(
                similarity__gt=0.3
            ).exclude(
                id__in=[p.id for p in products_list] + [p.id for p in same_category]
            ).order_by('-similarity', '-date')
            
            # Get products from the same brand
            brand_similar = Product.objects.filter(
                brand=first_match.brand
            ).exclude(
                id__in=[p.id for p in products_list] + [p.id for p in same_category] + [p.id for p in similar_categories]
            ).order_by('-date')
            
            # Combine all related products
            related_products = list(same_category) + list(similar_categories) + list(brand_similar)
        
        # If we have brand matches, get related products from the same brand and similar brands
        elif brand_matches:
            # Get products from the same brand
            same_brand = Product.objects.filter(
                brand=first_match.brand
            ).exclude(
                id__in=[p.id for p in products_list]
            ).order_by('-date')
            
            # Get products from similar brands
            similar_brands = Product.objects.annotate(
                similarity=TrigramSimilarity('brand__title', first_match.brand.title)
            ).filter(
                similarity__gt=0.3
            ).exclude(
                id__in=[p.id for p in products_list] + [p.id for p in same_brand]
            ).order_by('-similarity', '-date')
            
            # Get products from the same category
            category_similar = Product.objects.filter(
                category=first_match.category
            ).exclude(
                id__in=[p.id for p in products_list] + [p.id for p in same_brand] + [p.id for p in similar_brands]
            ).order_by('-date')
            
            # Combine all related products
            related_products = list(same_brand) + list(similar_brands) + list(category_similar)
        
        # If we only have description matches, get related products from the same category and brand
        elif description_matches and first_match.category:
            # Get products from the same category
            category_similar = Product.objects.filter(
                category=first_match.category
            ).exclude(
                id__in=[p.id for p in products_list]
            ).order_by('-date')
            
            # Get products from the same brand
            brand_similar = Product.objects.filter(
                brand=first_match.brand
            ).exclude(
                id__in=[p.id for p in products_list] + [p.id for p in category_similar]
            ).order_by('-date')
            
            # Combine all related products
            related_products = list(category_similar) + list(brand_similar)
    
    # If we still don't have any related products, try these fallbacks in order:
    if not related_products:
        # 1. Try to find products with similar titles
        title_similar = Product.objects.annotate(
            similarity=TrigramSimilarity('title', query)
        ).filter(
            similarity__gt=0.1
        ).exclude(
            id__in=[p.id for p in products_list]
        ).order_by('-similarity', '-date')
        
        # 2. Try to find products in similar categories
        category_similar = Product.objects.annotate(
            similarity=TrigramSimilarity('category__title', query)
        ).filter(
            similarity__gt=0.1
        ).exclude(
            id__in=[p.id for p in products_list] + [p.id for p in title_similar]
        ).order_by('-similarity', '-date')
        
        # 3. Try to find products with similar brands
        brand_similar = Product.objects.annotate(
            similarity=TrigramSimilarity('brand__title', query)
        ).filter(
            similarity__gt=0.1
        ).exclude(
            id__in=[p.id for p in products_list] + [p.id for p in title_similar] + [p.id for p in category_similar]
        ).order_by('-similarity', '-date')
        
        # 4. If still no matches, show recently added products
        if not any([title_similar, category_similar, brand_similar]):
            related_products = Product.objects.exclude(
                id__in=[p.id for p in products_list]
            ).order_by('-date')
        else:
            related_products = list(title_similar) + list(category_similar) + list(brand_similar)
    
    # Set up pagination for main results
    paginator = Paginator(products_list, 8)  # Show 8 or 12 products per page
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    # Set up pagination for related products
    related_paginator = Paginator(related_products, 8)  # Show 8 products per page
    related_page = request.GET.get('related_page', 1)
    related_products_page = related_paginator.get_page(related_page)
    
    context = {
        "products": products,
        "query": query,
        "related_products": related_products_page,
        "category_id": products_list[0].category.id if products_list and products_list[0].category else None
    }
    
    # Handle HTMX request for search results
    if request.headers.get('HX-Request'):
        if request.GET.get('related_page'):
            return render(request, 'core/partials/related_products.html', context)
        return render(request, 'core/partials/search_results.html', context)
    
    return render(request, "core/search.html", context)

def product_list_view(request):
    # Get all products and order by date
    products_list = Product.objects.all().order_by('-date')

    # Filtering logic
    category_ids = request.GET.getlist('category')
    brand_ids = request.GET.getlist('brand')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')

    if category_ids:
        products_list = products_list.filter(category__id__in=category_ids)
    if brand_ids:
        products_list = products_list.filter(brand__id__in=brand_ids)
    if price_min:
        products_list = products_list.filter(price__gte=price_min)
    if price_max:
        products_list = products_list.filter(price__lte=price_max)

    paginator = Paginator(products_list, 12)  # Show 12 products per page
    page = request.GET.get('page')
    products = paginator.get_page(page)

    categories = Category.objects.all()
    brands = Brand.objects.all()

    context = {
        "products": products,
        "categories": categories,
        "brands": brands,
        "selected_categories": [int(cid) for cid in category_ids],
        "selected_brands": [int(bid) for bid in brand_ids],
        "price_min": price_min,
        "price_max": price_max,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'core/partials/product_grid.html', context)

    return render(request, 'core/product-list.html', context)

def filter_products(request):
    """Filter products by category, brand, and price, return HTML for HTMX."""
    products = Product.objects.all().order_by('-date')

    category_ids = request.GET.getlist('category')
    brand_ids = request.GET.getlist('brand')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')

    if category_ids:
        products = products.filter(category__id__in=category_ids)
    if brand_ids:
        products = products.filter(brand__id__in=brand_ids)
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)

    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products_page = paginator.get_page(page)

    categories = Category.objects.all()
    brands = Brand.objects.all()

    context = {
        "products": products_page,
        "categories": categories,
        "brands": brands,
        "selected_categories": [int(cid) for cid in category_ids],
        "selected_brands": [int(bid) for bid in brand_ids],
        "price_min": price_min,
        "price_max": price_max,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'core/partials/product_grid.html', context)

    # fallback to JSON for non-HTMX requests (optional)
    return JsonResponse({'message': 'HTMX required'}, status=400)

@login_required
def dashboard_view(request):
    delivery_address = DeliveryAddress.objects.filter(user=request.user).first()
    # Fetch all orders placed by the user
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    # Count all orders placed by the user (not just the 5 most recent)
    total_orders_count = Order.objects.filter(user=request.user).count()
    context = {
        'delivery_address': delivery_address,
        'recent_orders': recent_orders,
        'total_orders_count': total_orders_count,
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status != 'Completed':  # Check if the order can be canceled
        order.status = 'Cancelled'
        order.save()
        messages.success(request, "Order has been canceled successfully.")
        return JsonResponse({'message': 'Order canceled successfully.'})
    else:
        messages.error(request, 'This order cannot be canceled as it is already completed.')
        return JsonResponse({'message': 'This order cannot be canceled as it is already completed.'}, status=400)

def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItems.objects.filter(order=order)
    items_data = [
        {
            "product_name": item.product.title,
            "quantity": item.quantity,
            "price": item.price
        }
        for item in order_items
    ]
    order_data = {
        "id": order.id,
        "amount": order.amount_paid,
        "status": order.status,
        "placed_on": order.created_at.isoformat(),
        "items": items_data
    }
    return JsonResponse(order_data)

@login_required
@ensure_csrf_cookie
def delivery_update_info_view(request):
    delivery_address, created = DeliveryAddress.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        try:
            form = DeliveryAddressForm(request.POST, instance=delivery_address)
            if form.is_valid():
                delivery_address = form.save()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Delivery address updated successfully.',
                        'delivery_data': {
                            'delivery_full_name': delivery_address.delivery_full_name,
                            'delivery_email': delivery_address.delivery_email,
                            'delivery_address': delivery_address.delivery_address,
                            'delivery_phone_number': delivery_address.delivery_phone_number,
                            'delivery_city': delivery_address.delivery_city,
                            'delivery_district': delivery_address.delivery_district,
                            'details_about_address': delivery_address.details_about_address
                        }
                    })
                else:
                    messages.success(request, "Delivery address updated successfully.")
                    return redirect("base:dashboard")
            else:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'errors': form.errors
                    }, status=400)
                messages.error(request, "Please correct the errors below.")
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                }, status=400)
            messages.error(request, str(e))
    else:
        form = DeliveryAddressForm(instance=delivery_address)
    
    context = {
        'form': form,
        'delivery_address': delivery_address
    }
    return render(request, 'core/update_info.html', context)

# API view for products
def api_products_view(request):
    """API endpoint for products, returns HTML for HTMX requests"""
    section = request.GET.get('section')
    page = request.GET.get('page', 1)
    
    # Handle categories section
    if section == 'categories':
        categories_list = Category.objects.all().order_by('id')
        paginator = Paginator(categories_list, 6)
        categories_page = paginator.get_page(page)
        
        # Render the categories section template
        html = render_to_string('core/partials/categories_section.html', {
            'categories': categories_page,
        }, request=request)
        
        return HttpResponse(html)
    
    # Ensure exactly 4 products per page for recent-products and best-selling
    per_page = {
        'daily-offer': 2,
        'recent-products': 4,
        'best-selling': 4,
        'special-products': 3,
        'monthly-products': 4,
    }.get(section, 4)
    
    # Get products based on section
    if section == 'daily-offer':
        products_list = Product.objects.filter(tags__name=Tag.DAILY_OFFER).order_by('-date')
        template_name = 'core/partials/daily_offer_products.html'
    elif section == 'recent-products':
        products_list = Product.objects.filter(tags__name=Tag.RECENT).order_by('-date', '-id')
        template_name = 'core/partials/recent_products.html'
    elif section == 'best-selling':
        products_list = Product.objects.filter(tags__name=Tag.BEST_SELLING_PRODUCT).order_by('-date', '-id')
        template_name = 'core/partials/best_selling_products.html'
    elif section == 'special-products':
        products_list = Product.objects.filter(tags__name=Tag.SPECIAL_PRODUCT).order_by('-date', '-id')
        template_name = 'core/partials/special_products.html'
    elif section == 'monthly-products':
        products_list = Product.objects.filter(tags__name=Tag.MONTHLY_PRODUCT).order_by('-date', '-id')
        template_name = 'core/partials/monthly_products.html'
    else:
        return JsonResponse({'error': 'Invalid section'}, status=400)
    
    # Paginate products
    paginator = Paginator(products_list, per_page)
    products_page = paginator.get_page(page)
    
    # Render the appropriate template with the paginated products
    html = render_to_string(template_name, {
        'products': products_page,
        'section': section
    }, request=request)
    
    return HttpResponse(html)

# New view for search suggestions
def search_suggestions(request):
    """AJAX endpoint for search suggestions"""
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    # Get exact title matches
    exact_matches = Product.objects.filter(title__iexact=query)
    
    # Get fuzzy title matches
    fuzzy_matches = Product.objects.annotate(
        similarity=TrigramSimilarity('title', query)
    ).filter(
        similarity__gt=0.3
    ).exclude(
        id__in=[p.id for p in exact_matches]
    ).order_by('-similarity')
    
    # Get category matches
    category_matches = Product.objects.filter(
        category__title__icontains=query
    ).exclude(
        id__in=[p.id for p in exact_matches] + [p.id for p in fuzzy_matches]
    )
    
    # Get brand matches
    brand_matches = Product.objects.filter(
        brand__title__icontains=query
    ).exclude(
        id__in=[p.id for p in exact_matches] + [p.id for p in fuzzy_matches] + [p.id for p in category_matches]
    )
    
    # Combine all matches
    all_matches = list(exact_matches) + list(fuzzy_matches) + list(category_matches) + list(brand_matches)
    
    # Limit to 5 suggestions
    suggestions = [{
        'id': product.id,
        'pid': product.pid,
        'title': product.title,
        'slug': product.slug,
        'image_url': product.get_image_url(),
        'price': str(product.price),
        'category': product.category.title if product.category else None,
        'brand': product.brand.title if product.brand else None
    } for product in all_matches[:5]]
    
    return JsonResponse({
        'query': query,
        'suggestions': suggestions,
        'count': len(suggestions)
    })

def related_products_view(request):
    """HTMX endpoint for related products pagination"""
    category_id = request.GET.get('category_id')
    page = request.GET.get('page', 1)
    
    if not category_id:
        return HttpResponse('')
    
    related_products = Product.objects.filter(
        category_id=category_id
    ).order_by('-date')
    
    paginator = Paginator(related_products, 8)  # Show 8 products per page
    products_page = paginator.get_page(page)
    
    return render(request, 'core/partials/related_products.html', {
        'related_products': products_page
    })


