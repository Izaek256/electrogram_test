import plotly.express as px
import plotly.graph_objects as go
from django.contrib import admin
from django.shortcuts import render
from django.urls import path
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Count, Sum, Avg
from django.conf import settings
from django.template.loader import select_template
from django.contrib.auth import get_user_model
from .models import UserActivity, Product, Order, Cart, ProductInteraction

User = get_user_model()  # Use the custom user model

class AnalyticsAdminSite(admin.AdminSite):
    site_header = "Website Analytics Dashboard"

    def dashboard_view(self, request):
        today = now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        # Total Users (Daily, Weekly, Monthly)
        daily_users = User.objects.filter(date_joined__date=today).count()
        weekly_users = User.objects.filter(date_joined__gte=week_ago).count()
        monthly_users = User.objects.filter(date_joined__gte=month_ago).count()
        total_users = User.objects.count()

        # Total Orders (Daily, Weekly, Monthly)
        daily_orders = Order.objects.filter(created_at__date=today).count()
        weekly_orders = Order.objects.filter(created_at__date__gte=week_ago).count()  # Fixed query
        monthly_orders = Order.objects.filter(created_at__date__gte=month_ago).count()  # Fixed query
        total_orders = Order.objects.count()

        # Abandoned Carts
        abandoned_carts = Cart.objects.filter(checked_out=False).count()

        # Average Time Spent on Site
        avg_time_spent = UserActivity.objects.aggregate(avg_time=Avg('time_spent'))['avg_time'] or 0

        # Most Searched Products
        searched_products = Product.objects.values('name').annotate(search_count=Sum('search_count')).order_by('-search_count')[:5]

        # Most Viewed & Clicked Products
        popular_products = ProductInteraction.objects.values('product__name').annotate(
            views=Sum('views'),
            clicks=Sum('clicks')
        ).order_by('-views')[:5]

        # Heatmap Data
        clicks = UserActivity.objects.values('click_x', 'click_y').annotate(count=Count('id'))
        heatmap_data = [{'x': c['click_x'], 'y': c['click_y'], 'count': c['count']} for c in clicks]

        # 📊 Bar Chart: Orders
        orders_chart = go.Figure(data=[
            go.Bar(name='Daily', x=['Orders'], y=[daily_orders], marker_color='blue'),
            go.Bar(name='Weekly', x=['Orders'], y=[weekly_orders], marker_color='green'),
            go.Bar(name='Monthly', x=['Orders'], y=[monthly_orders], marker_color='red'),
        ])
        orders_chart.update_layout(title="Orders Overview", barmode='group')

        # 📊 Pie Chart: Most Searched Products
        search_chart = px.pie(
            names=[p['name'] for p in searched_products],
            values=[p['search_count'] for p in searched_products],
            title="Most Searched Products"
        )

        # 📊 Bar Chart: Popular Products
        popular_chart = go.Figure(data=[
            go.Bar(
                x=[p['product__name'] for p in popular_products],
                y=[p['views'] for p in popular_products],
                name="Views",
                marker_color='purple'
            ),
            go.Bar(
                x=[p['product__name'] for p in popular_products],
                y=[p['clicks'] for p in popular_products],
                name="Clicks",
                marker_color='orange'
            ),
        ])
        popular_chart.update_layout(title="Most Viewed & Clicked Products", barmode='group')

        context = {
            'total_users': total_users,
            'daily_users': daily_users,
            'weekly_users': weekly_users,
            'monthly_users': monthly_users,
            'total_orders': total_orders,
            'daily_orders': daily_orders,
            'weekly_orders': weekly_orders,
            'monthly_orders': monthly_orders,
            'abandoned_carts': abandoned_carts,
            'avg_time_spent': avg_time_spent,
            'search_chart': search_chart.to_html(),
            'orders_chart': orders_chart.to_html(),
            'popular_chart': popular_chart.to_html(),
            'heatmap_data': heatmap_data
        }

        # Ensure the correct template is selected
        template = select_template(['analytics/analytics_dashboard.html'])
        return render(request, template.template.name, context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name="admin-dashboard"),
        ]
        return custom_urls + urls  # Merge custom and default URLs

# Register the custom admin site
admin_site = AnalyticsAdminSite(name="analytics_site")
admin.site = admin_site  # Replace the default admin site
