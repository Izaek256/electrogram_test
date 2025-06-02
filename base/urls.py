from django.urls import path, include
from .views import index, category_list_view, product_detail_view, delivery_update_info_view, product_category_list_view, search_view, product_list_view, filter_products, dashboard_view, cancel_order, order_detail_view, api_products_view, search_suggestions, related_products_view

app_name = "base"

urlpatterns = [
    path("", index, name="index"),
    path('products/', product_list_view, name='product_list'),  
    path("product/<slug:slug>", product_detail_view, name="product-detail"),
    path("category/", category_list_view, name="category_list"),
    path('cancel_order/<int:order_id>/', cancel_order, name='cancel_order'),
    path('api/orders/<int:order_id>/', order_detail_view, name='order_detail'),
    path("category/<cid>", product_category_list_view, name="product_category_list"),
    path("search/", search_view, name="search"),
    path("api/search-suggestions/", search_suggestions, name="search_suggestions"),
    path("filter-products/", filter_products, name="filter_products"),
    path("update_info/", delivery_update_info_view, name="delivery_update_info"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("api/products/", api_products_view, name="api_products"),
    path('related-products/', related_products_view, name='related-products'),
]
