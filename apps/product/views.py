import stripe
from django.http import Http404, JsonResponse
from django.views import View
from django.views.generic import TemplateView
from rest_framework import permissions, status, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum

from apps.dashboard.models import Order
from marketplace import settings
from .serializers import ProductSerializer, CartSerializer
from .models import Product, Cart
from apps.users.permissions import IsVendorPermission, IsOwnerOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class ProductCreateAPIView(APIView):
    permission_classes = [IsVendorPermission]
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = Product.objects.create(
                name=request.data['name'],
                vendor_id=request.data['vendor'],
                category_id=request.data['category'],
                description=request.data['description'],
                price=request.data['price']
            )
            product.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductAPIListPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'
    max_page_size = 1000
class ProductListAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        snippets = Product.objects.all()
        serializer = ProductSerializer(snippets, many=True)
        return Response(serializer.data)


class ProductFilterAPIView(generics.ListAPIView):
    pagination_class = ProductAPIListPagination
    permission_classes = [permissions.AllowAny]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    filterset_fields = ['price', 'name']
    search_fields = ['name', 'description']


class ProductDetailAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get_object(self, id):
        try:
            return Product.objects.get(id=id)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, id):
        snippet = self.get_object(id)
        serializer = ProductSerializer(snippet)
        return Response(serializer.data)


class ProductUpdateAPIView(APIView):
    permission_classes = [IsVendorPermission, IsOwnerOrReadOnly]

    def get_object(self, id):
        try:
            return Product.objects.get(id=id)
        except Product.DoesNotExist:
            raise Http404

    def put(self, request, id):
        snippet = self.get_object(id)
        serializer = ProductSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDeleteAPIView(APIView):
    permission_classes = [IsVendorPermission, IsOwnerOrReadOnly]

    def get_object(self, id):
        try:
            return Product.objects.get(id=id)
        except Product.DoesNotExist:
            raise Http404

    def delete(self, request, id):
        snippet = self.get_object(id)
        snippet.delete()
        return Response(status.HTTP_204_NO_CONTENT)


class AddToCartAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get_object(self, user_id):
        try:
            return Cart.objects.get(customer_id=user_id)
        except Cart.DoesNotExist:
            raise Http404

    def put(self, request, user_id):
        snippet = self.get_object(user_id)
        serializer = CartSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartDetailAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    # authentication_classes = []
    # parser_classes = JSONParser

    def get_object(self, user_id):
        try:
            return Cart.objects.get(customer_id=user_id)
        except Cart.DoesNotExist:
            raise Http404

    def get(self, request, user_id):
        cart = self.get_object(user_id)
        serializer1 = CartSerializer(cart)
        serializer2 = ProductSerializer(cart.product.all(), many=True)
        data = serializer1.data
        data['product'] = serializer2.data
        return Response(data, status=status.HTTP_200_OK)


stripe.api_key = settings.STRIPE_SECRET_KEY

class CreateCheckoutSessionView(View):
    def get_object(self, user_id):
        try:
            return Cart.objects.get(customer_id=user_id)
        except Cart.DoesNotExist:
            raise Http404
    def post(self,request, *args, **kwargs):
        product_id = self.kwargs["pk"]
        cart = self.get_object(product_id)
        # product = ProductSerializer(cart.product.all(), many=True)
        # Cart.objects.aggregate(Sum('price'))
        price = cart.product.all().aggregate(Sum('price'))
        print(price)

        product = {}
        product['id'] = product_id
        product['name'] = 'order'
        product['price'] = price


        order = Order.objects.create(
            name=product['name']+str(Order.pk),
            price=product['price']['price__sum']
        )
        order.save()

        # product_id = '020323'
        # product = Product.objects.get(id=product_id)
        YOUR_DOMAIN = "http://127.0.0.1:8000"
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': product['price']['price__sum']*100,
                        'product_data': {
                            'name': product['name']
                        },
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                "product_id": product['id']
            },
            mode='payment',
            success_url=YOUR_DOMAIN + '/success/',
            cancel_url=YOUR_DOMAIN + '/cancel/',
        )
        return JsonResponse({
            'id': checkout_session.id
        })

class SuccessView(TemplateView):
    template_name = "success.html"

class CancelView(TemplateView):
    template_name = "cancel.html"

class ProductLandingPageView(TemplateView):
    template_name = "landing.html"

    def get_context_data(self, **kwargs):
        product = Product.objects.get(name="twix")
        context = super(ProductLandingPageView, self).get_context_data(**kwargs)
        context.update({
            "product": product,
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY
        })
        return context

class PayToCartAPIView(TemplateView):
    permission_classes = [permissions.AllowAny]
    template_name = "landing.html"
    def get_object(self, user_id):
        try:
            return Cart.objects.get(customer_id=user_id)
        except Cart.DoesNotExist:
            raise Http404
    def get_context_data(self, user_id, **kwargs):
        cart = self.get_object(user_id)
        # product = ProductSerializer(cart.product.all(), many=True)
        # Cart.objects.aggregate(Sum('price'))
        price=cart.product.all().aggregate(Sum('price'))

        product={}
        product['id']=user_id
        product['name']='order'
        product['price']=price
        context = super(PayToCartAPIView, self).get_context_data(  **kwargs)
        context.update({
            "product": product,
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY
        })
        return context
    # def get(self, request, user_id):
    #     snippet = self.get_object(user_id)
    #     serializer = CartSerializer(snippet, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # def get(self, request, user_id):
    #     cart = self.get_object(user_id)
    #     serializer1 = CartSerializer(cart)
    #     serializer2 = ProductSerializer(cart.product.all(), many=True)
    #     data = serializer1.data
    #     data['product'] = serializer2.data
    #     return Response(data, status=status.HTTP_200_OK)
