import jwt
from django.http import Http404
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework_simplejwt import exceptions
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import filters
from marketplace.settings import SECRET_KEY
from .serializer import VendorSerializer, CustomerSerializer, MyTokenObtainPairSerializer
from .models import Vendor, Customer
from rest_framework import permissions, status, generics
from .permissions import AnonPermission
from product.models import Cart, Product
from product.serializers import CartSerializer, ProductSerializer


class LoginView(TokenObtainPairView):
    permission_classes = (AnonPermission,)
    serializer_class = MyTokenObtainPairSerializer


def decode_auth_token(token):
    try:
        user=jwt.decode(token,SECRET_KEY,algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        msg='Signature has expired.Login again'
    except jwt.DecodeError:
        msg='Error decoding signature.Type valid token'
        raise exceptions.AuthenticationFailed(msg)
    except jwt.InvalidTokenError:
        raise exceptions.AuthenticationFailed()
    return user


class VendorRegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    # authentication_classes = []
    # parser_classes = JSONParser

    def post(self, request):
        serializer = VendorSerializer(data=request.data)
        if serializer.is_valid():
            vendor = Vendor.objects.create(
                email=request.data['email'],
                is_Vendor=True,
                name=request.data['name'],
                second_name=request.data['second_name'],
                phone_number=request.data['phone_number'],
                description=request.data['description']
            )
            vendor.set_password(request.data['password'])
            vendor.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    # authentication_classes = []
    # parser_classes = JSONParser

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            customer = Customer.objects.create(
                email=request.data['email'],
                name=request.data['name'],
                second_name=request.data['second_name'],
                phone_number=request.data['phone_number'],
                cart_number=request.data['cart_number'],
                address=request.data['address'],
                post_code=request.data['post_code'],
            )
            customer.set_password(request.data['password'])
            customer.save()
            cart = Cart.objects.create(
                customer=customer
            )
            cart.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VendorListAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    # authentication_classes = []

    def get(self, request):
        snippets = Vendor.objects.all()
        serializer = VendorSerializer(snippets, many=True)
        return Response(serializer.data)


class CustomerListAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    # authentication_classes = []

    def get(self, request):
        snippets = Customer.objects.all()
        serializer = CustomerSerializer(snippets, many=True)
        return Response(serializer.data)

class VendorProfileAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    # authentication_classes = []

    def get_object(self, token):
        try:
            user=decode_auth_token(token)
            return Vendor.objects.get(id=user['user_id'])
        except Vendor.DoesNotExist:
            raise Http404

    def get_object_id(self,token):
        try:
            user=decode_auth_token(token)
            return user['user_id']
        except Vendor.DoesNotExist:
            raise Http404
    def get(self, request, token):
        # snippet = self.get_object(token)
        # serializer = CustomerSerializer(snippet)
        # return Response(serializer.data)
        snippet = self.get_object(token)
        id=self.get_object_id(token)
        products = Product.objects.filter(vendor_id=id)
        serializer = VendorSerializer(snippet)
        # serializer2 = CartSerializer(products)
        serializer3 = ProductSerializer(products.all(), many=True)
        data = serializer.data
        # cart_data = serializer2.data
        # cart_data['product'] = serializer3.data
        data['product'] = serializer3.data
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, token):
        snippet = self.get_object(token)
        serializer = VendorSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, token):
        snippet = self.get_object(token)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
class VendorDetailAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    # authentication_classes = []

    def get_object(self, id):
        try:
            return Vendor.objects.get(id=id)
        except Vendor.DoesNotExist:
            raise Http404

    def get(self, request, id):
        snippet = self.get_object(id)
        serializer = VendorSerializer(snippet)
        return Response(serializer.data)

    def put(self, request, id):
        snippet = self.get_object(id)
        serializer = VendorSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        snippet = self.get_object(id)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomerDetailAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    # authentication_classes = []

    def get_object(self, id):
        try:
            return Customer.objects.get(id=id)
        except Customer.DoesNotExist:
            raise Http404

    def get(self, request, id):
        snippet = self.get_object(id)
        cart = Cart.objects.get(customer_id=id)
        serializer = CustomerSerializer(snippet)
        serializer2 = CartSerializer(cart)
        serializer3 = ProductSerializer(cart.product.all(), many=True)
        data = serializer.data
        cart_data = serializer2.data
        cart_data['product'] = serializer3.data
        data['cart'] = cart_data
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, id):
        snippet = self.get_object(id)
        serializer = CustomerSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        snippet = self.get_object(id)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomerProfileAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    # authentication_classes = []

    def get_object(self, token):
        try:
            user=decode_auth_token(token)
            return Customer.objects.get(id=user['user_id'])
        except Customer.DoesNotExist:
            raise Http404
    def get_object_id(self,token):
        try:
            user=decode_auth_token(token)
            return user['user_id']
        except Customer.DoesNotExist:
            raise Http404
    def get(self, request, token):
        # snippet = self.get_object(token)
        # serializer = CustomerSerializer(snippet)
        # return Response(serializer.data)
        snippet = self.get_object(token)
        id=self.get_object_id(token)
        cart = Cart.objects.get(customer_id=id)
        serializer = CustomerSerializer(snippet)
        serializer2 = CartSerializer(cart)
        serializer3 = ProductSerializer(cart.product.all(), many=True)
        data = serializer.data
        cart_data = serializer2.data
        cart_data['product'] = serializer3.data
        data['cart'] = cart_data
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, token):
        snippet = self.get_object(token)
        serializer = CustomerSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, token):
        snippet = self.get_object(token)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProductAPIListPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'
    max_page_size = 1000
class UserFilterAPIView(generics.ListAPIView):
    pagination_class = ProductAPIListPagination
    permission_classes = [permissions.AllowAny]
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    filterset_fields = ['name', 'cart_number']
    search_fields = ['name', 'description']