from django.shortcuts import render
from .models import Cart, CartItem
from rest_framework import generics, permissions, authentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializer import CartSerializer, CartItemSerializer
from product.models import Product
from rest_framework.response import Response
from rest_framework import status


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

    def perform_create(self, serializer):
        user = self.request.user
        cart, created = Cart.objects.get_or_create(owner=user)
        product_id = self.request.data.get('product')
        quantity = self.request.data.get('quantity', 1)
        product = Product.objects.get(id=product_id)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += int(quantity)
            cart_item.save()
        else:
            serializer.save(cart=cart, product=product, quantity=quantity)


class CartItemIncrementAPIView(generics.UpdateAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    authentication_classes = [authentication.SessionAuthentication, JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = self.request.user
        cart_item = self.get_object()
        if cart_item.cart.owner != user:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        cart_item.quantity += 1
        cart_item.save()
        serializer = self.get_serializer(cart_item)
        return Response(serializer.data)


class CartItemDecrementAPIView(generics.UpdateAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    authentication_classes = [authentication.SessionAuthentication, JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = self.request.user
        cart_item = self.get_object()
        if cart_item.cart.owner != user:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        cart_item.quantity -= 1
        if cart_item.quantity <= 0:
            cart_item.delete()
            return Response({"detail": "Cart item deleted."}, status=status.HTTP_204_NO_CONTENT)
        cart_item.save()
        serializer = self.get_serializer(cart_item)
        return Response(serializer.data)