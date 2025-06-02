from django.urls import path
from .views import track_click
from .admin import admin_site

urlpatterns = [
    path('track-click/', track_click, name='track_click'), # Register the custom admin site
]
