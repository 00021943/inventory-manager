from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category
from orders.models import Order, OrderItem
from .forms import UserRegisterForm


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(
                request, f"Account created for {username}! You can now login."
            )
            return redirect("login")
    else:
        form = UserRegisterForm()
    return render(request, "registration/register.html", {"form": form})


def store_home(request):
    featured_products = Product.objects.order_by("-created_at")[:4]
    cart = request.session.get("cart", {})
    return render(
        request,
        "store/home.html",
        {"featured_products": featured_products, "cart": cart},
    )


def product_catalog(request):
    category_id = request.GET.get("category")
    if category_id:
        products = Product.objects.filter(category_id=category_id)
    else:
        products = Product.objects.all()

    categories = Category.objects.all()
    cart = request.session.get("cart", {})

    return render(
        request,
        "store/catalog.html",
        {
            "products": products,
            "categories": categories,
            "current_category": int(category_id) if category_id else None,
            "cart": cart,
        },
    )


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = request.session.get("cart", {})
    return render(
        request, "store/product_detail.html", {"product": product, "cart": cart}
    )


def add_to_cart(request, pk):
    from django.http import JsonResponse

    product = get_object_or_404(Product, pk=pk)
    cart = request.session.get("cart", {})

    # Check available stock
    current_quantity = cart.get(str(pk), 0)
    if current_quantity >= product.stock_quantity:
        message = (
            f"Only {product.stock_quantity} items available in stock. Cannot add more."
        )
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": False,
                    "message": message,
                    "quantity": current_quantity,
                    "stock_quantity": product.stock_quantity,
                }
            )
        messages.warning(request, message)
        return redirect(request.META.get("HTTP_REFERER", "product_catalog"))

    cart[str(pk)] = current_quantity + 1
    request.session["cart"] = cart
    request.session.modified = True

    message = "Item added to cart"
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "success": True,
                "message": message,
                "quantity": cart[str(pk)],
                "stock_quantity": product.stock_quantity,
                "product_id": pk,
            }
        )

    messages.success(request, message)
    return redirect(request.META.get("HTTP_REFERER", "product_catalog"))


def view_cart(request):
    cart = request.session.get("cart", {})
    cart_items = []
    total_price = 0
    has_stock_issues = False

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(pk=product_id)
            available_stock = product.stock_quantity
            requested_quantity = quantity

            # Check if requested quantity exceeds available stock
            if requested_quantity > available_stock:
                has_stock_issues = True
                messages.warning(
                    request,
                    f"{product.name}: Only {available_stock} available, but {requested_quantity} in cart. Please adjust quantity.",
                )

            subtotal = product.price * min(requested_quantity, available_stock)
            total_price += subtotal
            cart_items.append(
                {
                    "product": product,
                    "quantity": requested_quantity,
                    "available_stock": available_stock,
                    "subtotal": subtotal,
                    "has_stock_issue": requested_quantity > available_stock,
                }
            )
        except Product.DoesNotExist:
            # Product was deleted, remove from cart
            if str(product_id) in cart:
                del cart[str(product_id)]
            messages.warning(
                request,
                f"Product with ID {product_id} no longer exists and was removed from cart.",
            )

    request.session["cart"] = cart

    return render(
        request,
        "store/cart.html",
        {
            "cart_items": cart_items,
            "total_price": total_price,
            "has_stock_issues": has_stock_issues,
        },
    )


def update_cart_quantity(request, pk, action):
    from django.http import JsonResponse

    product = get_object_or_404(Product, pk=pk)
    cart = request.session.get("cart", {})
    product_key = str(pk)
    current_quantity = cart.get(product_key, 0)

    success = False
    message = ""
    new_quantity = current_quantity

    if action == "increase":
        # Check if we can add more items
        if current_quantity >= product.stock_quantity:
            message = f"Only {product.stock_quantity} items available in stock. Cannot add more."
            success = False
        else:
            cart[product_key] = current_quantity + 1
            new_quantity = cart[product_key]
            success = True
            message = "Item added to cart"
    elif action == "decrease":
        if product_key in cart:
            cart[product_key] = cart[product_key] - 1
            if cart[product_key] <= 0:
                del cart[product_key]
                new_quantity = 0
            else:
                new_quantity = cart[product_key]
            success = True
            message = "Quantity updated"

    request.session["cart"] = cart
    request.session.modified = True

    # Return JSON response for AJAX requests
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "success": success,
                "message": message,
                "quantity": new_quantity,
                "stock_quantity": product.stock_quantity,
                "product_id": pk,
            }
        )

    # Fallback for non-AJAX requests
    if success:
        messages.success(request, message)
    else:
        messages.warning(request, message)
    return redirect(request.META.get("HTTP_REFERER", "product_catalog"))


def remove_from_cart(request, pk):
    cart = request.session.get("cart", {})
    if str(pk) in cart:
        del cart[str(pk)]
        request.session["cart"] = cart
    return redirect("view_cart")


@login_required
def checkout(request):
    cart = request.session.get("cart", {})
    if not cart:
        messages.warning(request, "Your cart is empty")
        return redirect("product_catalog")

    # Validate stock availability before creating order
    errors = []
    cart_items_to_check = []

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(pk=product_id)
            if quantity > product.stock_quantity:
                errors.append(
                    f"{product.name}: Only {product.stock_quantity} available, but {quantity} requested."
                )
            elif quantity <= 0:
                errors.append(f"{product.name}: Invalid quantity.")
            else:
                cart_items_to_check.append({"product": product, "quantity": quantity})
        except Product.DoesNotExist:
            errors.append(f"Product with ID {product_id} not found.")

    # If there are errors, show them and redirect back to cart
    if errors:
        for error in errors:
            messages.error(request, error)
        return redirect("view_cart")

    # All validations passed, create order
    order = Order.objects.create(user=request.user, status="pending")

    for item in cart_items_to_check:
        product = item["product"]
        quantity = item["quantity"]

        OrderItem.objects.create(
            order=order, product=product, price=product.price, quantity=quantity
        )

        # Deduct stock - ensure it doesn't go negative
        product.stock_quantity = max(0, product.stock_quantity - quantity)
        product.save()

    # Clear cart
    request.session["cart"] = {}
    messages.success(request, "Order placed successfully!")
    return redirect("my_orders")


@login_required
def order_history(request):
    """
    Display order history for the current logged-in user.
    Shows only orders belonging to the current user.
    """
    # Filter orders by user - shows ONLY current user's orders
    # Using explicit user_id check to ensure security - no other users' orders should be visible
    orders = (
        Order.objects.filter(user=request.user)
        .select_related("user")
        .prefetch_related("items__product")
        .order_by("-created_at")
    )

    return render(
        request,
        "store/order_history.html",
        {"orders": orders, "current_user": request.user},
    )
