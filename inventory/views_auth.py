from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def customer_login(request):
    """Login page for customers - staff can also login here"""
    if request.user.is_authenticated:
        return redirect('product_catalog')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'product_catalog')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please provide both username and password.')
    
    return render(request, 'registration/login.html', {'is_customer_login': True})

@login_required
def customer_logout(request):
    """Logout from customer account - accepts both GET and POST"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('product_catalog')
