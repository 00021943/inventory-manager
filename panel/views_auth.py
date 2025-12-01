from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def panel_login(request):
    """Login page specifically for staff panel"""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('panel:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_staff:
                    login(request, user)
                    next_url = request.GET.get('next', 'panel:dashboard')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Access denied. Staff access only.')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please provide both username and password.')
    
    return render(request, 'panel/login.html')

@login_required
def panel_logout(request):
    """Logout from panel"""
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('panel:panel_login')
