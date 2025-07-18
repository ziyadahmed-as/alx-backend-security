# ip_tracking/urls.py
from django.urls import path
from .views import public_api_view, private_api_view, login_view

urlpatterns = [
    path('api/public/', public_api_view, name='public-api'),
    path('api/private/', private_api_view, name='private-api'),
    path('login/', login_view, name='login'),
]