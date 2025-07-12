from django.db import models
from django.contrib.auth.models import User
from product.models import Product
from .constants import *
from address.models import Address


PAYMENT_STATUS_CHOICES = [
    (PAYMENT_PENDING, 'Pending'),
    (PAYMENT_PAID, 'Paid'),
    (PAYMENT_FAILED, 'Failed'),
]


DELIVERY_STATUS_CHOICES = [
    (DELIVERY_PROCESSING, 'Processing'),
    (DELIVERY_SHIPPED, 'Shipped'),
    (DELIVERY_DELIVERED, 'Delivered'),
    (DELIVERY_CANCELLED, 'Cancelled'),
]

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    shipping_address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name='shipping_address', null=True)
    billing_address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name='billing_addres', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_PENDING)
    delivery_status = models.CharField(max_length=20, choices=DELIVERY_STATUS_CHOICES, default=DELIVERY_PROCESSING)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} order"

    @property
    def total_price(self) -> float:
        return sum(item.price * item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)


