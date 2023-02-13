from django.http import JsonResponse
from django.shortcuts import render
from apps.dashboard.models import Order
from django.core import serializers

from apps.product.models import Product
from apps.users.models import Customer, Vendor


def dashboard_with_pivot(request):
    return render(request, 'dashboard_with_pivot.html', {})


def dashboard_with_pivot_vendors(request):
    return render(request, 'dashboard_vendor.html', {})
def dashboard_with_pivot_orders(request):
    return render(request, 'dashboard_vendor.html', {})


def dashboard_with_pivot_customers(request):
    return render(request, 'dashboard_customer.html', {})



def pivot_data(request):
    dataset = Product.objects.all()
    data=serializers.serialize('json',dataset)
    return JsonResponse(data, safe=False)

def pivot_data_vendor(request):
    dataset = Vendor.objects.all()
    data = serializers.serialize('json', dataset)
    return JsonResponse(data, safe=False)
def pivot_data_vendor(request):
    dataset = Order.objects.all()
    data = serializers.serialize('json', dataset)
    return JsonResponse(data, safe=False)

def pivot_data_customer(request):
    dataset = Customer.objects.all()
    data = serializers.serialize('json', dataset)
    return JsonResponse(data, safe=False)