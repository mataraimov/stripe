from django.contrib import admin

from dashboard.models import Order
from .models import Category, Product, Cart

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Order)