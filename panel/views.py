from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from orders.models import Order, OrderItem
from inventory.models import Product, Category
from .forms import StaffCreationForm, StaffUpdateForm, ProductForm, CategoryForm

def staff_required(user):
    """Check if user is staff member"""
    return user.is_staff

@login_required
@user_passes_test(staff_required)
def dashboard(request):
    """Main dashboard view for staff"""
    # Get statistics for today
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    # Order statistics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    completed_orders = Order.objects.filter(status='completed').count()
    cancelled_orders = Order.objects.filter(status='cancelled').count()
    
    # Today's statistics
    today_orders = Order.objects.filter(created_at__date=today).count()
    today_revenue = Order.objects.filter(
        created_at__date=today,
        status='completed'
    ).aggregate(total=Sum('items__price'))['total'] or 0
    
    # Week statistics
    week_orders = Order.objects.filter(created_at__date__gte=week_ago).count()
    week_revenue = Order.objects.filter(
        created_at__date__gte=week_ago,
        status='completed'
    ).aggregate(total=Sum('items__price'))['total'] or 0
    
    # Recent orders
    recent_orders = Order.objects.all().order_by('-created_at')[:10]
    
    # Low stock products (less than 10 items)
    low_stock_products = Product.objects.filter(stock_quantity__lt=10).order_by('stock_quantity')[:5]
    
    # Top selling products - count by quantity sold from completed orders only
    from django.db.models import Q
    top_products = Product.objects.annotate(
        total_sold=Sum(
            'order_items__quantity',
            filter=Q(order_items__order__status__in=['completed', 'processing'])
        )
    ).filter(total_sold__isnull=False, total_sold__gt=0).order_by('-total_sold')[:5]
    
    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'cancelled_orders': cancelled_orders,
        'today_orders': today_orders,
        'today_revenue': today_revenue,
        'week_orders': week_orders,
        'week_revenue': week_revenue,
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products,
        'top_products': top_products,
    }
    
    return render(request, 'panel/dashboard.html', context)

@login_required
@user_passes_test(staff_required)
def order_management(request):
    """View for managing all orders"""
    status_filter = request.GET.get('status', '')
    
    orders = Order.objects.all()
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    orders = orders.order_by('-created_at')
    
    context = {
        'orders': orders,
        'current_status': status_filter,
    }
    
    return render(request, 'panel/order_management.html', context)

@login_required
@user_passes_test(staff_required)
def order_detail_panel(request, pk):
    """Detailed view of an order with management options"""
    order = get_object_or_404(Order, pk=pk)
    
    context = {
        'order': order,
    }
    
    return render(request, 'panel/order_detail.html', context)

@login_required
@user_passes_test(staff_required)
def update_order_status(request, pk, status):
    """Update order status"""
    order = get_object_or_404(Order, pk=pk)
    
    if status in ['pending', 'processing', 'completed', 'cancelled']:
        old_status = order.status
        order.status = status
        order.save()
        
        # If order is cancelled, restore stock
        if status == 'cancelled' and old_status != 'cancelled':
            for item in order.items.all():
                product = item.product
                product.stock_quantity += item.quantity
                product.save()
        
        messages.success(request, f'Order #{order.id} status updated to {status}')
    else:
        messages.error(request, 'Invalid status')
    
    return redirect('panel:order_detail', pk=pk)

@login_required
@user_passes_test(staff_required)
def inventory_management(request):
    """View for managing inventory"""
    category_filter = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    
    products = Product.objects.all()
    
    if category_filter:
        products = products.filter(category_id=category_filter)
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    products = products.order_by('name')
    categories = Category.objects.all()
    
    # Calculate statistics
    total_products = products.count()
    out_of_stock = products.filter(stock_quantity=0).count()
    low_stock = products.filter(stock_quantity__lt=10, stock_quantity__gt=0).count()
    
    context = {
        'products': products,
        'categories': categories,
        'current_category': category_filter,
        'search_query': search_query,
        'total_products': total_products,
        'out_of_stock': out_of_stock,
        'low_stock': low_stock,
    }
    
    return render(request, 'panel/inventory_management.html', context)

@login_required
@user_passes_test(staff_required)
def update_stock(request, pk):
    """Quick stock update"""
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        new_stock = request.POST.get('stock_quantity')
        
        if new_stock and new_stock.isdigit():
            product.stock_quantity = int(new_stock)
            product.save()
            messages.success(request, f'Stock updated for {product.name}')
        else:
            messages.error(request, 'Invalid stock quantity')
    
    return redirect('panel:inventory_management')

@login_required
@user_passes_test(staff_required)
def staff_management(request):
    """View for managing staff members"""
    staff_members = User.objects.filter(is_staff=True).order_by('-date_joined')
    
    # Calculate statistics properly
    total_staff = staff_members.count()
    active_staff = staff_members.filter(is_active=True).count()
    super_admins = staff_members.filter(is_superuser=True).count()
    
    context = {
        'staff_members': staff_members,
        'total_staff': total_staff,
        'active_staff': active_staff,
        'super_admins': super_admins,
    }
    
    return render(request, 'panel/staff_management.html', context)

@login_required
@user_passes_test(staff_required)
def staff_create(request):
    """Create a new staff member"""
    if request.method == 'POST':
        form = StaffCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Staff member {user.username} created successfully!')
            return redirect('panel:staff_management')
    else:
        form = StaffCreationForm()
    
    return render(request, 'panel/staff_form.html', {'form': form, 'title': 'Create Staff Member'})

@login_required
@user_passes_test(staff_required)
def staff_edit(request, pk):
    """Edit an existing staff member"""
    staff_member = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        form = StaffUpdateForm(request.POST, instance=staff_member)
        if form.is_valid():
            form.save()
            messages.success(request, f'Staff member {staff_member.username} updated successfully!')
            return redirect('panel:staff_management')
    else:
        form = StaffUpdateForm(instance=staff_member)
    
    return render(request, 'panel/staff_form.html', {'form': form, 'title': f'Edit Staff Member: {staff_member.username}'})

@login_required
@user_passes_test(staff_required)
def staff_toggle_status(request, pk):
    """Toggle staff member active status"""
    staff_member = get_object_or_404(User, pk=pk)
    
    # Don't allow deactivating yourself
    if staff_member == request.user:
        messages.error(request, "You cannot deactivate your own account!")
        return redirect('panel:staff_management')
    
    staff_member.is_active = not staff_member.is_active
    staff_member.save()
    
    status = "activated" if staff_member.is_active else "deactivated"
    messages.success(request, f'Staff member {staff_member.username} has been {status}!')
    
    return redirect('panel:staff_management')

@login_required
@user_passes_test(staff_required)
def staff_delete(request, pk):
    """Delete a staff member"""
    staff_member = get_object_or_404(User, pk=pk)
    
    # Don't allow deleting yourself
    if staff_member == request.user:
        messages.error(request, "You cannot delete your own account!")
        return redirect('panel:staff_management')
    
    # Don't allow deleting superusers (for safety)
    if staff_member.is_superuser:
        messages.error(request, "Cannot delete superuser accounts!")
        return redirect('panel:staff_management')
    
    if request.method == 'POST':
        username = staff_member.username
        staff_member.delete()
        messages.success(request, f'Staff member {username} has been deleted successfully!')
        return redirect('panel:staff_management')
    
    return render(request, 'panel/staff_confirm_delete.html', {'staff_member': staff_member})

@login_required
@user_passes_test(staff_required)
def customer_management(request):
    """View for managing customers"""
    search_query = request.GET.get('search', '')
    
    # Get all users who are not staff (customers)
    customers_base = User.objects.filter(is_staff=False)
    
    if search_query:
        customers_base = customers_base.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Calculate statistics before annotation
    total_customers = customers_base.count()
    active_customers = customers_base.filter(is_active=True).count()
    customers_with_orders = customers_base.filter(orders__isnull=False).distinct().count()
    
    # Get order statistics for each customer
    customers = customers_base.annotate(
        total_orders=Count('orders'),
        total_spent=Sum('orders__items__price', filter=Q(orders__status='completed'))
    ).order_by('-date_joined')
    
    context = {
        'customers': customers,
        'total_customers': total_customers,
        'active_customers': active_customers,
        'customers_with_orders': customers_with_orders,
        'search_query': search_query,
    }
    
    return render(request, 'panel/customer_management.html', context)

@login_required
@user_passes_test(staff_required)
def customer_detail(request, pk):
    """Detailed view of a customer with their orders"""
    customer = get_object_or_404(User, pk=pk, is_staff=False)
    
    # Get customer's orders
    orders = Order.objects.filter(user=customer).order_by('-created_at')
    
    # Calculate statistics
    total_orders = orders.count()
    completed_orders = orders.filter(status='completed').count()
    pending_orders = orders.filter(status='pending').count()
    total_spent = sum(order.total_price for order in orders.filter(status='completed'))
    
    context = {
        'customer': customer,
        'orders': orders,
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'pending_orders': pending_orders,
        'total_spent': total_spent,
    }
    
    return render(request, 'panel/customer_detail.html', context)

@login_required
@user_passes_test(staff_required)
def customer_toggle_status(request, pk):
    """Toggle customer active status"""
    customer = get_object_or_404(User, pk=pk, is_staff=False)
    
    customer.is_active = not customer.is_active
    customer.save()
    
    status = "activated" if customer.is_active else "deactivated"
    messages.success(request, f'Customer {customer.username} has been {status}!')
    
    return redirect('panel:customer_management')

@login_required
@user_passes_test(staff_required)
def profile(request):
    """View for staff to see their own profile"""
    user = request.user
    
    # Get user's order statistics
    total_orders = Order.objects.filter(user=user).count()
    completed_orders = Order.objects.filter(user=user, status='completed').count()
    pending_orders = Order.objects.filter(user=user, status='pending').count()
    
    # Get recent orders
    recent_orders = Order.objects.filter(user=user).order_by('-created_at')[:5]
    
    context = {
        'user': user,
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'pending_orders': pending_orders,
        'recent_orders': recent_orders,
    }
    
    return render(request, 'panel/profile.html', context)

# Product Management Views
@login_required
@user_passes_test(staff_required)
def product_management(request):
    """View for managing products - list, create, edit, delete"""
    products = Product.objects.select_related('category').order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(name__icontains=search_query)
    
    # Category filter
    category_filter = request.GET.get('category', '')
    if category_filter:
        products = products.filter(category_id=category_filter)
    
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
    }
    
    return render(request, 'panel/product_management.html', context)

@login_required
@user_passes_test(staff_required)
def product_create(request):
    """Create a new product"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" created successfully!')
            return redirect('panel:product_management')
    else:
        form = ProductForm()
    
    return render(request, 'panel/product_form.html', {'form': form, 'title': 'Create Product'})

@login_required
@user_passes_test(staff_required)
def product_edit(request, pk):
    """Edit an existing product"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('panel:product_management')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'panel/product_form.html', {'form': form, 'product': product, 'title': 'Edit Product'})

@login_required
@user_passes_test(staff_required)
def product_delete(request, pk):
    """Delete a product"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('panel:product_management')
    
    return render(request, 'panel/product_confirm_delete.html', {'product': product})

# Category Management Views
@login_required
@user_passes_test(staff_required)
def category_management(request):
    """View for managing categories"""
    categories = Category.objects.annotate(
        product_count=Count('products')
    ).order_by('name')
    
    return render(request, 'panel/category_management.html', {'categories': categories})

@login_required
@user_passes_test(staff_required)
def category_create(request):
    """Create a new category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" created successfully!')
            return redirect('panel:category_management')
    else:
        form = CategoryForm()
    
    return render(request, 'panel/category_form.html', {'form': form, 'title': 'Create Category'})

@login_required
@user_passes_test(staff_required)
def category_edit(request, pk):
    """Edit an existing category"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" updated successfully!')
            return redirect('panel:category_management')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'panel/category_form.html', {'form': form, 'category': category, 'title': 'Edit Category'})

@login_required
@user_passes_test(staff_required)
def category_delete(request, pk):
    """Delete a category"""
    category = get_object_or_404(Category, pk=pk)
    
    # Check if category has products
    if category.products.exists():
        messages.error(request, f'Cannot delete category "{category.name}" because it has products. Please delete or move products first.')
        return redirect('panel:category_management')
    
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'Category "{category_name}" deleted successfully!')
        return redirect('panel:category_management')
    
    return render(request, 'panel/category_confirm_delete.html', {'category': category})
