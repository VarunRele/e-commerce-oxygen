from django.contrib import admin
from .models import Order
from .constants import *
from django.utils.html import format_html




@admin.action(description='Mark selected orders as Shipped')
def mark_as_shipped(self, request, queryset):
    updated = queryset.update(delivery_status=DELIVERY_SHIPPED)
    self.message_user(request, f"{updated} order(s) marked as shipped.")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'created_at', 'payment_status', 'delivery_status']
    list_editable = ['delivery_status']
    list_filter = ['payment_status', 'delivery_status', 'created_at']
    search_fields = ['user__username', 'id']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    actions = [mark_as_shipped]

    def colored_delivery_status(self, obj):
        color = {
            DELIVERY_PROCESSING: 'orange',
            DELIVERY_SHIPPED: 'blue',
            DELIVERY_DELIVERED: 'green',
            DELIVERY_CANCELLED: 'red'
        }.get(obj.delivery_status, 'black')
        return format_html('<span style="color: {};">{}</span>', color, obj.delivery_status)
    colored_delivery_status.short_description = 'Delivery Status'