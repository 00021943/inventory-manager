from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_count']
    search_fields = ['name']
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'name', 'category', 'price', 'stock_status']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['price']
    readonly_fields = ['image_preview_large']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return "-"
    image_preview.short_description = 'Image'

    def image_preview_large(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 300px;" />', obj.image.url)
        return "-"
    image_preview_large.short_description = 'Current Image'

    def stock_status(self, obj):
        if obj.stock_quantity == 0:
            return format_html('<span style="color: red; font-weight: bold;">Out of Stock</span>')
        elif obj.stock_quantity < 10:
            return format_html('<span style="color: orange; font-weight: bold;">Low Stock ({})</span>', obj.stock_quantity)
        return format_html('<span style="color: green;">In Stock ({})</span>', obj.stock_quantity)
    stock_status.short_description = 'Stock'

