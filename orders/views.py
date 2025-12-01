from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from .forms import OrderItemForm
from inventory.models import Product

@login_required
def order_list(request):
    # Client-side: ALWAYS show only current user's orders
    # For viewing all orders, use /panel/orders/ (panel:order_management)
    # This ensures separation between client and admin views
    orders = Order.objects.filter(user=request.user).select_related('user').prefetch_related('items__product').order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})

@login_required
def my_orders(request):
    # Show only current user's orders - filtered at database level
    orders = Order.objects.filter(user=request.user).select_related('user').prefetch_related('items__product').order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})

@login_required
def order_detail(request, pk):
    # Only allow users to view their own orders (unless they are staff)
    if request.user.is_staff:
        # Staff can view any order
        order = get_object_or_404(Order, pk=pk)
    else:
        # Regular users can only view their own orders
        order = get_object_or_404(Order, pk=pk, user=request.user)
    # View-only mode - no adding or deleting items allowed
    return render(request, 'orders/order_detail.html', {'order': order})

@login_required
def order_item_delete(request, order_pk, item_pk):
    item = get_object_or_404(OrderItem, pk=item_pk, order_id=order_pk)
    if request.method == 'POST':
        # Restore stock
        product = item.product
        product.stock_quantity += item.quantity
        product.save()
        
        item.delete()
        return redirect('order_detail', pk=order_pk)
    return render(request, 'orders/order_item_confirm_delete.html', {'item': item, 'order': item.order})
