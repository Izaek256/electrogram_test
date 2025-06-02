from django.contrib import admin
from .models import DeliveryAddress, Order, OrderItems


class OrderItemInline(admin.TabularInline):
    model = OrderItems
    extra = 1
    fields = ('product', 'quantity', 'price', 'total')
    readonly_fields = ('order_id_email',)


    def order_id_email(self, obj):
        return f"Order ID: {obj.order.id}, User Email: {obj.order.email}"
    order_id_email.short_description = 'Order ID and User Email'


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'amount_paid', 'status', 'order_date')
    inlines = [OrderItemInline]

    # Custom method to display user email
    def user_email(self, obj):
        return obj.user.email if obj.user else 'No User Email'
    user_email.short_description = 'User Email'

    # Add user email to the right-hand side in admin list view
    def get_list_display(self, request):
        return super().get_list_display(request) + ('user_email',)


admin.site.register(DeliveryAddress)
admin.site.register(Order, OrderAdmin)
