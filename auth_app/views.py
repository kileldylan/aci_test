from datetime import timedelta

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.http import require_POST
from .forms import CustomLoginForm
from .models import LoginAttempt

#trigger_fail

LOGIN_FAILURE_LIMIT = 5
LOGIN_LOCKOUT_DURATION = timedelta(minutes=15)


def _login_is_locked(email):
    last_success = (
        LoginAttempt.objects.filter(email__iexact=email, success=True)
        .order_by("-timestamp", "-pk")
        .first()
    )
    failures = LoginAttempt.objects.filter(email__iexact=email, success=False)
    if last_success is not None:
        failures = failures.filter(
            Q(timestamp__gt=last_success.timestamp)
            | Q(timestamp=last_success.timestamp, pk__gt=last_success.pk)
        )

    if failures.count() < LOGIN_FAILURE_LIMIT:
        return False

    latest_failure = failures.order_by("-timestamp", "-pk").first()
    return (
        latest_failure is not None
        and timezone.now() < latest_failure.timestamp + LOGIN_LOCKOUT_DURATION
    )


def login_view(request):
    """Login page with email and password"""
    if request.user.is_authenticated:
        return redirect('auth_app:dashboard')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            if _login_is_locked(email):
                messages.error(request, "Invalid email or password")
            else:
                try:
                    user = User.objects.get(email__iexact=email)
                except User.DoesNotExist:
                    user = None

                if user is not None:
                    user_auth = authenticate(
                        request,
                        username=user.username,
                        password=password,
                    )

                    if user_auth is not None:
                        login(request, user_auth)
                        LoginAttempt.objects.create(
                            user=user,
                            email=email,
                            success=True,
                            ip_address=request.META.get('REMOTE_ADDR')
                        )
                        messages.success(
                            request,
                            f"Welcome back, {user.username}!",
                        )
                        return redirect('auth_app:dashboard')

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
    last_successful_login = (
        LoginAttempt.objects.filter(user=request.user, success=True)
        .order_by("-timestamp")
        .first()
    )
    recent_successful_logins = LoginAttempt.objects.filter(
        user=request.user,
        success=True,
    ).order_by("-timestamp", "-pk")[:5]
    return render(request, 'auth_app/dashboard.html', {
        'user': request.user,
        'last_successful_login': last_successful_login,
        'recent_successful_logins': recent_successful_logins,
    })

@require_POST
def logout_view(request):
    """Logout user"""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('auth_app:login')

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