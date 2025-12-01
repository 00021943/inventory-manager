from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0
    readonly_fields = ['get_cost']

    def get_cost(self, obj):
        return f"${obj.get_cost()}"
    get_cost.short_description = 'Subtotal'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_info', 'status_badge', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'user__email', 'id']
    inlines = [OrderItemInline]
    readonly_fields = ['total_amount']

    def customer_info(self, obj):
        if obj.user:
            return f"{obj.user.username} ({obj.user.email})"
        return "N/A"
    customer_info.short_description = 'Customer'

    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'completed': 'green',
            'cancelled': 'red',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 10px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def total_amount(self, obj):
        return f"${obj.total_price}"
    total_amount.short_description = 'Total'
