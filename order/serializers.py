from rest_framework import serializers
from .models import Order, OrderItem
from address.models import Address

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    shipping_address = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all())
    billing_address = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all(), required=False, allow_null=True)
    items = OrderItemSerializer(many=True, read_only=True)
    order_id = serializers.IntegerField(source='id', read_only=True)
    class Meta:
        model = Order
        fields = ['order_id', 'user', 'shipping_address', 'billing_address', 'created_at', 'payment_status', 'delivery_status', 'items', 'total_price']
        read_only_fields = ['created_at']

    def validate_shipping_address(self, value):
        if value.user != self.context['request'].user:
            raise serializers.ValidationError("You do not own this shipping address.")
        return value

    def validate_billing_address(self, value):
        if value and value.user != self.context['request'].user:
            raise serializers.ValidationError("You do not own this billing address.")
        return value