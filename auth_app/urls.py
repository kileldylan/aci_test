from django.urls import path
from . import views
from . import api_views        

app_name = 'auth_app'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('api/auth/health/', views.auth_health_check, name='auth_health'),
    path('health', views.auth_health_check, name='health'),
    path('api/login/', api_views.api_login, name='api_login'),   
]