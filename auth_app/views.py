from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .forms import CustomLoginForm
from .models import LoginAttempt
import json

def login_view(request):
    """Login page with email and password"""
    if request.user.is_authenticated:
        return redirect('auth_app:dashboard')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Try to find user by email
            try:
                user = User.objects.get(email=email)
                user_auth = authenticate(request, username=user.username, password=password)
                
                if user_auth is not None:
                    login(request, user_auth)
                    
                    # Log successful attempt
                    LoginAttempt.objects.create(
                        user=user,
                        email=email,
                        success=True,
                        ip_address=request.META.get('REMOTE_ADDR')
                    )
                    
                    messages.success(request, f"Welcome back, {user.username}!")
                    return redirect('auth_app:dashboard')
                else:
                    # Invalid password
                    LoginAttempt.objects.create(
                        email=email,
                        success=False,
                        ip_address=request.META.get('REMOTE_ADDR')
                    )
                    messages.error(request, "Invalid email or password")
                    
            except User.DoesNotExist:
                # User not found
                LoginAttempt.objects.create(
                    email=email,
                    success=False,
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                messages.error(request, "Invalid email or password")
        else:
            messages.error(request, "Invalid email or password")
    else:
        form = CustomLoginForm()
    
    return render(request, 'auth_app/login.html', {'form': form})

@login_required
def dashboard_view(request):
    """Dashboard after successful login"""
    return render(request, 'auth_app/dashboard.html', {
        'user': request.user
    })

def logout_view(request):
    """Logout user"""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('auth_app:login')

# deploy to test
# API endpoint for ACI verification
@csrf_exempt
def auth_health_check(request):
    """Health check endpoint for ACI to verify auth is working"""
    if request.method == 'GET':
        return JsonResponse({
            'status': 'ok',
            'auth_enabled': True,
            'login_url': '/login/',
            'dashboard_url': '/dashboard/'
        })
    return JsonResponse({'error': 'Method not allowed'}, status=405)