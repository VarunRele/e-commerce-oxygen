from django.shortcuts import render, get_object_or_404
import razorpay.errors
from rest_framework import status
from .models import Order, OrderItem
from cart.models import Cart, CartItem
from .serializers import OrderSerializer
from rest_framework import generics, permissions, authentication
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from .permission import IsOwnerOrAdmin
from .constants import *
import razorpay
from django.conf import settings


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


class CancelOrderAPIView(APIView):
    """
    Cancel an order with a given ID, only if it's in PROCESSING or SHIPPED state.
    """
    authentication_classes = [authentication.SessionAuthentication, JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        self.check_object_permissions(request, order)

        if order.delivery_status not in [DELIVERY_PROCESSING, DELIVERY_SHIPPED]:
            return Response({"detail": "Cannot cancel this order"}, status=status.HTTP_400_BAD_REQUEST)

        order.delivery_status = DELIVERY_CANCELLED
        order.save()
        return Response({"detail": "Order cancelled"}, status=status.HTTP_200_OK)



class CreateRazorPayOrderAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request, pk: int):
        user = request.user
        order = get_object_or_404(Order, pk=pk, user=user)

        if order.payment_status != PAYMENT_PENDING:
            return Response({"detail": "Payment already processed."}, status=status.HTTP_400_BAD_REQUEST)

        client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
        amount = int(order.total_price) * 100
        razorpay_order = client.order.create(data = {
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1
        })
        order.razorpay_order_id = razorpay_order['id']
        order.save()
        return Response({
            "razorpay_order_id": razorpay_order['id'],
            "amount": amount,
            "key_id": settings.RAZORPAY_API_KEY
        })


class VerifyRazorPayPaymentAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request: Request):
        user = request.user
        data = request.data

        order = get_object_or_404(Order, razorpay_order_id=data['razorpay_order_id'])
        client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature': data['razorpay_signature']
            })
        except razorpay.errors.SignatureVerificationError:
            return Response({"detail": "Signature verification failed."}, status=status.HTTP_400_BAD_REQUEST)

        order.razorpay_payment_id = data['razorpay_payment_id']
        order.razorpay_signature = data['razorpay_signature']
        order.payment_status = PAYMENT_PAID
        order.save()

        return Response({"detail": "Payment verified and order complete"}, status=status.HTTP_200_OK)