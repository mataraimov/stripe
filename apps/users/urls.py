from django.urls import path
from .views import (
    VendorRegisterView,
    CustomerRegisterView,
    VendorListAPIView,
    CustomerListAPIView,
    LoginView,
    VendorDetailAPIView,
    CustomerDetailAPIView, VendorProfileAPIView, CustomerProfileAPIView, UserFilterAPIView,
)

urlpatterns = [
    path('vendor/register/', VendorRegisterView.as_view(), name='vendor-register'),
    path('customer/register/', CustomerRegisterView.as_view(), name='customer-register'),
    path('vendor/list/', VendorListAPIView.as_view(), name='vendor-list'),
    path('customer/list/', CustomerListAPIView.as_view(), name='customer-list'),
    path('login/', LoginView.as_view(), name='login'),
    path('customer/<int:id>/', CustomerDetailAPIView.as_view(), name='customer-detail'),
    path('vendor/<int:id>/', VendorDetailAPIView.as_view(), name='vendor-detail'),
    path('vendor/profile/<str:token>/', VendorProfileAPIView.as_view(), name='vendor-profile'),
    path('customer/profile/<str:token>/', CustomerProfileAPIView.as_view(), name='customer-profile'),
    path('filter/', UserFilterAPIView.as_view(), name='user-filter'),
]