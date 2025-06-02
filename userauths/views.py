from django.shortcuts import render, redirect
from cart.cart import Cart
from payments.views import process_order
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from userauths.forms import UserRegisterForm, LoginForm, ChangePasswordForm, ProfileForm
from .models import User, Profile
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from django.views.decorators.csrf import ensure_csrf_cookie
from django.urls import reverse

@ensure_csrf_cookie
def signup_view(request):
    form = UserRegisterForm()
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            try:
                new_user = form.save(commit=False)
                new_user.set_password(form.cleaned_data['password1'])
                new_user.save()
                messages.success(request, 'Welcome! Your account has been created successfully. You are now logged in.')
                login(request, new_user, backend='django.contrib.auth.backends.ModelBackend')
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Welcome! Your account has been created successfully.',
                        'redirect_url': '/delivery-update-info/'
                    })
                return redirect('base:delivery_update_info')
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': str(e)
                    }, status=400)
                messages.error(request, str(e))
                return render(request, 'userauths/sign_up.html', {'form': form})
            
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    return render(request, 'userauths/sign_up.html', {'form': form})

@ensure_csrf_cookie
def sign_in(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Welcome back! You have been logged in successfully.')
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Welcome back! You have been logged in successfully.',
                        'redirect_url': '/'
                    })
                return redirect('base:index')
            else:
                form.add_error(None, "Invalid username or password.")
                messages.error(request, "Unable to log in. Please check your email and password and try again.")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
        return render(request, 'userauths/sign_in.html', {'form': form})
    else:
        form = LoginForm()
    return render(request, 'userauths/sign_in.html', {'form': form})

def logout_view(request):
    cart = Cart(request)
    if cart.get_quants():
        try:
            process_order(request)
            messages.success(request, 'Your cart items have been saved as an order. You can view them in your order history.')
        except Exception as e:
            messages.error(request, 'We encountered an issue saving your cart items. Please try again or contact support.')
    logout(request)
    messages.info(request, 'You have been logged out successfully. Thank you for shopping with us!')
    return redirect('userauths:sign_in')

@ensure_csrf_cookie
def profile_update_view(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        profile_form = ProfileForm(request.POST or None, instance=current_user)

        if request.method == 'POST':
            try:
                if profile_form.is_valid():
                    # Save the user data
                    user = profile_form.save()
                    
                    # Get or create profile and update it
                    profile, created = Profile.objects.get_or_create(user=user)
                    profile.username = user.username
                    profile.email = user.email
                    profile.first_name = user.first_name
                    profile.last_name = user.last_name
                    profile.save()

                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': True,
                            'message': 'Your profile has been updated successfully!',
                            'user_data': {
                                'username': user.username,
                                'email': user.email,
                                'first_name': user.first_name,
                                'last_name': user.last_name
                            }
                        })
                    messages.success(request, "Your profile has been updated successfully!")
                    return redirect("base:index")
                else:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'errors': profile_form.errors
                        }, status=400)
                    messages.error(request, "Please correct the errors below.")
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': str(e)
                    }, status=400)
                messages.error(request, str(e))

        return render(request, 'userauths/profile_update.html', {'profile_form': profile_form})
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Please log in to access your profile settings.'
            }, status=401)
        messages.error(request, "Please log in to access your profile settings.")
        return redirect("userauths:sign_in")

@ensure_csrf_cookie
def password_update_view(request):
    if request.user.is_authenticated:
        current_user = request.user
        if request.method == "POST":
            try:
                form = ChangePasswordForm(current_user, request.POST)
                if form.is_valid():
                    form.save()
                    messages.success(request, "Your password has been updated successfully. Please sign in with your new password.")
                    
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': True,
                            'message': 'Your password has been updated successfully. Please sign in with your new password.',
                            'redirect_url': reverse('userauths:sign_in')
                        })
                    
                    # Log out the user after password change
                    logout(request)
                    return redirect("userauths:sign_in")
                else:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'errors': form.errors
                        }, status=400)
                    for error in list(form.errors.values()):
                        messages.error(request, f"Password update failed: {error}")
                    return redirect("userauths:password_update")
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': str(e)
                    }, status=400)
                messages.error(request, str(e))
        else:
            form = ChangePasswordForm(current_user)
            return render(request, 'userauths/update_password.html', {'form': form})
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Please log in to change your password.'
            }, status=401)
        messages.error(request, "Please log in to change your password.")
        return redirect("userauths:sign_in")




