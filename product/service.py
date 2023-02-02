from django_filters import rest_framework as filters

from product.models import Product
#
#
# class CharFilterinFilter(filters.BaseInFilter,filters.CharFilter):
#     pass
#
#
# class ProductFilter(filters.FilterSet):
#     products=CharFilterinFilter(field_name='category__name',lookup_expr='in')
#     price=filters.RangeFilter()
#
#     class Meta:
#         model = Product
#         fields = ['category','price']
class ProductFilter(filters.FilterSet):
    price=filters.RangeFilter()

    class Meta:
        model = Product
        fields = [ 'price']