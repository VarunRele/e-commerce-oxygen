from django.shortcuts import render, get_object_or_404
from .models import Cart, CartItem
from rest_framework import generics, permissions, authentication
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializer import CartSerializer, CartItemSerializer
from product.models import Product
from rest_framework.response import Response
from rest_framework import status
from .permissions import IsOwnerOrAdmin


class CartListAPIView(generics.ListAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    authentication_classes = [authentication.SessionAuthentication, JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Cart.objects.filter(owner=user)


class CartItemCreateAPIView(generics.CreateAPIView):
    serializer_class = CartItemSerializer
    authentication_classes = [authentication.SessionAuthentication, JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = self.request.user
        cart, created = Cart.objects.get_or_create(owner=user)
        product_id = self.request.data.get('product')
        quantity = self.request.data.get('quantity', 1)
        product = get_object_or_404(Product, id=product_id)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += int(quantity)
            cart_item.save()
            serializer = self.get_serializer(cart_item)
            return Response(serializer.data, status=status.HTTP_200_OK)

        cart_item.quantity = int(quantity)
        cart_item.save()
        serializer = self.get_serializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartItemUpdateAPIView(APIView):
    authentication_classes = [authentication.SessionAuthentication, JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    value = 0

    def post(self, request, pk):
        cart_item = get_object_or_404(CartItem, pk=pk)
        if cart_item.cart.owner != request.user:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

        cart_item.quantity += self.value
        if cart_item.quantity <= 0:
            cart_item.delete()
            return Response({"detail": "Cart item deleted."}, status=status.HTTP_204_NO_CONTENT)

        cart_item.save()
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CartItemIncrementAPIView(CartItemUpdateAPIView):
    value = 1

class CartItemDecrementAPIView(CartItemUpdateAPIView):
    value = -1


class CartItemDestoryAPIView(generics.DestroyAPIView):
    queryset = CartItem.objects.all()
    authentication_classes = [authentication.SessionAuthentication, JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]