from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from . import views

app_name = 'auth_app'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='auth_app/password_reset_form.html',
            email_template_name='auth_app/password_reset_email.html',
            subject_template_name='auth_app/password_reset_subject.txt',
            success_url=reverse_lazy('auth_app:password_reset_done'),
        ),
        name='password_reset',
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='auth_app/password_reset_done.html',
        ),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='auth_app/password_reset_confirm.html',
            success_url=reverse_lazy('auth_app:password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path(
        'reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='auth_app/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('api/auth/health/', views.auth_health_check, name='auth_health'),
]