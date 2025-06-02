from django.urls import path
from .views import sign_in, signup_view, logout_view, profile_update_view, password_update_view
from django.contrib.auth import views as auth_views

app_name = "userauths"

urlpatterns = [
    path('sign_in/', sign_in, name='sign_in'),
    path('sign_up/', signup_view, name='sign_up'),
    path('sign_out/', logout_view, name='sign_out'),
    path('profile_update/', profile_update_view, name='user_profile_update'),
    path('update_password/', password_update_view, name='password_update'),
    
    # Password reset
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='userauths/password_reset.html',
             email_template_name='userauths/password_reset_email.html',
             success_url='/user/password-reset/done/'  # Hard-coded URL path
         ), 
         name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='userauths/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='userauths/password_reset_confirm.html',
             success_url='/user/password-reset-complete/'  # Hard-coded URL path
         ), 
         name='password_reset_confirm'),
    
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='userauths/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]