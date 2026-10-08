from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('receipts', views.ReceiptViewSet, basename='receipts')

urlpatterns = [
    path('', include(router.urls)),

    path("auth/login", views.api_login, name="api_login"),
    path('auth/logout', views.api_logout, name='api_logout'),
    path('auth/me', views.api_me, name='api_me'),
    path('config/', views.api_config, name='api_config'),
    path('csrf/', views.api_csrf, name='api_csrf'),
]
