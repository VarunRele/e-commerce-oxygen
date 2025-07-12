from django.shortcuts import render
from rest_framework import status
from .models import Order, OrderItem
from cart.models import Cart, CartItem
from .serializers import OrderSerializer
from rest_framework import generics, permissions, authentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from .permission import IsOwnerOrAdmin
from .constants import *

class OrderCreateAPIView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = [authentication.SessionAuthentication, JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = self.request.user
        cart = Cart.objects.prefetch_related('items').get(owner=user)
        if not cart.items.exists():
            return Response({"detail": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        user = self.request.user
        cart = Cart.objects.prefetch_related('items').get(owner=user)
        instance = serializer.save(user=user)
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order = instance,
                product = cart_item.product,
                quantity = cart_item.quantity,
                price = cart_item.product.price
            )
        cart.items.all().delete()

    def list(self, request, *args, **kwargs):
        user = self.request.user
        if not user.is_staff:
            self.queryset = Order.objects.filter(user=user)
        return super().list(request, *args, **kwargs)


class OrderRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = [authentication.SessionAuthentication, JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]


class CancelOrderAPIView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = [authentication.SessionAuthentication, JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        if order.delivery_status not in [DELIVERY_PROCESSING, DELIVERY_SHIPPED]:
            return Response({"detail": "Cannot cancel this order"}, status=status.HTTP_400_BAD_REQUEST)
        order.delivery_status = DELIVERY_CANCELLED
        order.save()
        return Response({"detail": "Order cancel"}, status=status.HTTP_200_OK)

