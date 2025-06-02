from django.contrib import admin
from analytics.admin import admin_site
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.views import serve
from django.views.static import serve as static_serve
from django.urls import re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('analytics/', include('analytics.urls')),
    path('', include('base.urls')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('payment/', include('payments.urls', namespace='payments')),
    path('user/', include('userauths.urls', namespace='userauths')),
]

if settings.DEBUG:
    # Serve static files from development server
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {
            'document_root': settings.STATICFILES_DIRS[0],
        }),
    ]
    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)