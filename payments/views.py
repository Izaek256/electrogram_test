from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import json
from .models import DeliveryAddress
from .models import Order

from .forms import DeliveryAddressForm
from datetime import timedelta
from django.http import HttpResponse

from .models import Order, OrderItems
from django.contrib import messages
from django.db import transaction
from django.db.models import Max
from base.models import Product
import logging
from cart.cart import Cart
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from payments.utils.twilio_whatsapp import send_whatsapp_message
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.core.mail import EmailMessage

from django.utils import timezone
from django.views.decorators.http import require_GET
import qrcode
import base64

logger = logging.getLogger(__name__)

@login_required
def billing_info(request):
    if not request.user.is_authenticated:
        logger.error("Unauthenticated user attempted to access billing info")
        messages.error(request, "Please log in to access your billing information.")
        return redirect("userauths:sign-in")
    
    try:
        delivery_address, created = DeliveryAddress.objects.get_or_create(user=request.user)
        logger.debug(f"Delivery address {'created' if created else 'retrieved'} for user {request.user.id}")
    except Exception as e:
        logger.error(f"Error getting/creating delivery address for user {request.user.id}: {str(e)}")
        messages.error(request, "We're having trouble loading your billing information. Please try again or contact support.")
        return redirect("payments:billing-info")

    if request.method == 'POST':
        form = DeliveryAddressForm(request.POST, instance=delivery_address)
        if form.is_valid():
            request.session['my_delivery'] = {
                'delivery_full_name': form.cleaned_data.get('delivery_full_name'),
                'delivery_email': form.cleaned_data.get('delivery_email'),
                'delivery_address': form.cleaned_data.get('delivery_address'),
                'delivery_phone_number': form.cleaned_data.get('delivery_phone_number'),
                'delivery_city': form.cleaned_data.get('delivery_city'),
                'delivery_district': form.cleaned_data.get('delivery_district'),
                'details_about_address': form.cleaned_data.get('details_about_address')
            }

            try:
                delivery_address = form.save(commit=False)
                if not request.user.is_authenticated:
                    logger.error("User authentication lost during form submission")
                    messages.error(request, "Your session has expired. Please log in again to continue.")
                    return redirect("userauths:sign-in")
                
                delivery_address.user = request.user
                delivery_address.full_clean()
                delivery_address.save()
                logger.info(f"Successfully saved delivery address for user {request.user.id}")
                messages.success(request, "Your delivery information has been saved successfully. You can now proceed to checkout.")
            except Exception as e:
                logger.error(f"Error saving delivery address for user {request.user.id}: {str(e)}")
                messages.error(request, "We couldn't save your delivery information. Please check your details and try again.")
                return redirect("payments:billing-info")

            return redirect("payments:checkout")
    else:
        form = DeliveryAddressForm(instance=delivery_address)

    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()

    context = {
        'cart_products': cart_products,
        'quantities': quantities,
        'totals': totals,
        'form': form,
        'delivery_address': delivery_address
    }
    
    return render(request, 'payments/billing_info.html', context)


@login_required
def recent_orders_count(request):
    recent_orders = Order.objects.count()  # Count all orders
    return recent_orders
@login_required
def dashboard_view(request):
    delivery_address = DeliveryAddress.objects.filter(user=request.user).first()
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]  # Fetch latest 5 orders
    recent_orders_count = Order.objects.filter(user=request.user).count()  # Count recent orders
    context = {
        'delivery_address': delivery_address,
        'recent_orders': recent_orders,
        'recent_orders_count': recent_orders_count,  # Add recent orders count to context
    }
    return render(request, 'core/dashboard.html', context)
    return Order.objects.count()  # Count all orders

def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    file_name = f"qr_codes/{data['order_id']}_qr.png"
    file_path = default_storage.save(file_name, ContentFile(buffer.getvalue()))
    return default_storage.url(file_path)

def generate_qr_code_base64(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    base64_img = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{base64_img}"

@login_required
def order_success(request):    
    context = {}  # Initialize context

    if request.user.is_authenticated:
        try:
            order = Order.objects.filter(user=request.user).latest('created_at')
            order_items = OrderItems.objects.filter(order=order)
            
            if not order.due_date:
                order.due_date = order.invoice_date + timedelta(days=7)
                order.save()
                
            try:
                delivery_address = DeliveryAddress.objects.get(user=order.user)
                context = {
                    'order': order,
                    'order_items': order_items,
                    'company_info': order.company_info.split('\n'),
                    'invoice_date': order.invoice_date.strftime('%B %d, %Y'),
                    'due_date': order.due_date.strftime('%B %d, %Y'),
                    'pdf_url': f'/generate-pdf/{order.id}/',
                    'phone_number': delivery_address.delivery_phone_number,
                    'delivery_address': delivery_address
                }
            except DeliveryAddress.DoesNotExist:
                context = {
                    'order': order,
                    'order_items': order_items,
                    'company_info': order.company_info.split('\n'),
                    'invoice_date': order.invoice_date.strftime('%B %d, %Y'),
                    'due_date': order.due_date.strftime('%B %d, %Y'),
                    'pdf_url': f'/generate-pdf/{order.id}/',
                    'phone_number': 'Not provided',
                    'delivery_address': None
                }

            try:
                context['recent_orders_count'] = recent_orders_count(request)  # Add recent orders count to context
            except Exception as e:
                logger.error(f"Error fetching recent orders count: {str(e)}")
                context['recent_orders_count'] = 0  # Default to 0 if there's an error

            qr_data = {
                'user_id': request.user.id,
                'order_id': order.id,
                'dashboard_url': request.build_absolute_uri('/dashboard/')
            }
            qr_code_url = generate_qr_code(qr_data)
            context['qr_code_url'] = qr_code_url

            return render(request, 'payments/order_success.html', context)

        except Order.DoesNotExist:
            messages.error(request, "No order found.")
            return redirect("base:index")

    else:
        messages.error(request, "You must be logged in to view order details.")
        return redirect("userauths:sign-in")


@login_required
def process_order(request):
    if request.method == 'POST':
        cart = Cart(request)
        quantities = cart.get_quants()
        total = cart.cart_total()
        session_key = request.session.session_key

        logger.debug(f"Cart quantities before processing: {quantities}")
        logger.debug(f"Cart total before processing: {total}")

        if not quantities:
            messages.error(request, "Your cart is empty. Please add items before checking out.")
            return redirect("payments:checkout")

        try:
            user = request.user if request.user.is_authenticated else None
            if not request.user.is_authenticated:
                messages.error(request, "You must be logged in to create an order.")
                return redirect("userauths:sign-in")

            # Check if delivery address is complete
            try:
                delivery_address = DeliveryAddress.objects.get(user=request.user)
                if not all([
                    delivery_address.delivery_address,
                    delivery_address.delivery_city,
                    delivery_address.delivery_district,
                    delivery_address.delivery_phone_number
                ]):
                    messages.error(request, "Please complete your delivery address before placing an order.")
                    return redirect("payments:billing-info")
            except DeliveryAddress.DoesNotExist:
                messages.error(request, "Please set up your delivery address before placing an order.")
                return redirect("payments:billing-info")

            with transaction.atomic():
                max_order_id = Order.objects.aggregate(max_id=Max('id'))['max_id']
                logger.debug(f"Current max order id: {max_order_id}")

                # Use delivery information for the order creation
                order = Order.objects.create(
                    user=user,
                    full_name=delivery_address.delivery_full_name,
                    email=delivery_address.delivery_email,
                    amount_paid=total,
                    status='pending',
                    session_key=session_key
                )

                logger.info(f"Created order {order.id} for user {user.id if user else 'guest'} with {len(quantities)} items")

                for product_id, item in quantities.items():
                    try:
                        product = Product.objects.get(id=product_id)
                        OrderItems.objects.create(
                            order=order,
                            product=product,
                            quantity=item['quantity'],
                            price=product.price,
                            total=product.price * item['quantity']
                        )
                    except Product.DoesNotExist:
                        continue

                # Clear cart
                cart.clear()
                request.session.modified = True

                # Prepare context for email
                order_items = OrderItems.objects.filter(order=order)
                invoice_date = order.invoice_date.strftime('%B %d, %Y') if order.invoice_date else ''
                due_date = order.due_date.strftime('%B %d, %Y') if order.due_date else ''
                phone_number = delivery_address.delivery_phone_number if delivery_address else ''
                qr_data = {
                    'user_id': user.id,
                    'order_id': order.id,
                    'dashboard_url': request.build_absolute_uri('/dashboard/')
                }
                # Generate QR code as base64 for email attachment
                try:
                    import qrcode
                    import base64
                    from io import BytesIO
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(json.dumps(qr_data))
                    qr.make(fit=True)
                    img = qr.make_image(fill='black', back_color='white')
                    buffer = BytesIO()
                    img.save(buffer, format="PNG")
                    base64_img = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    qr_code_url = f"data:image/png;base64,{base64_img}"
                except Exception as e:
                    logger.error(f"Error generating QR code: {str(e)}", exc_info=True)
                    qr_code_url = ''

                # Context for customer email
                customer_context = {
                    'order': order,
                    'order_items': order_items,
                    'invoice_date': invoice_date,
                    'due_date': due_date,
                    'phone_number': phone_number,
                    'qr_code_url': qr_code_url,
                }
                
                # Send email to customer
                customer_html_content = render_to_string('payments/order_email.html', customer_context)
                customer_subject = f"Order Confirmation - Invoice #{order.invoice_number}"
                from_email = settings.DEFAULT_FROM_EMAIL
                to_email = [order.email]
                customer_email = EmailMultiAlternatives(customer_subject, strip_tags(customer_html_content), from_email, to_email)
                customer_email.attach_alternative(customer_html_content, "text/html")
                
                # If QR code was successfully generated, attach it as a separate file
                if qr_code_url:
                    try:
                        # Extract base64 data and convert back to binary
                        qr_binary = base64.b64decode(base64_img)
                        customer_email.attach(f"Your Order QR Code.png", qr_binary, 'image/png')
                    except Exception as e:
                        logger.error(f"Error attaching QR code: {str(e)}", exc_info=True)
                
                customer_email.send()
                
                # Send notification to admin
                admin_context = {
                    'order': order,
                    'order_items': order_items,
                    'user': user,
                    'delivery_address': delivery_address,
                    'phone_number': phone_number,
                    'invoice_date': invoice_date,
                    'due_date': due_date,
                    'qr_code_url': qr_code_url,
                }
                
                admin_html_content = render_to_string('payments/admin_order_notification.html', admin_context)
                admin_subject = f"New Order Notification - Invoice #{order.invoice_number}"
                admin_email = settings.EMAIL_HOST_USER  # Send to the admin email configured in settings
                
                admin_notification = EmailMultiAlternatives(admin_subject, strip_tags(admin_html_content), from_email, [admin_email])
                admin_notification.attach_alternative(admin_html_content, "text/html")
                admin_notification.send()

                messages.success(request, "Order placed successfully! A detailed invoice has been sent to your email.")
                return redirect('payments:order-success')

        except Exception as e:
            logger.error(f"Error processing order: {str(e)}", exc_info=True)
            messages.error(request, f"An error occurred while processing your order: {str(e)}")
            return redirect("payments:billing_info")
    return redirect("payments:billing_info")
