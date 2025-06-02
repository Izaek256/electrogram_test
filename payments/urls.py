from django.urls import path
from . import views


app_name = "payments"

urlpatterns = [
    path("billing_info/", views.billing_info, name="billing_info"),
    path("process_order/", views.process_order, name="process_order"),
    path("order-success/", views.order_success, name="order-success"),
]
