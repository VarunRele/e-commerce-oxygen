from rest_framework import serializers
from .models import Cart, CartItem
from product.serializer import ProductSerializer
from product.models import Product

class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True
    )
    product_detail = ProductSerializer(source='product', read_only=True)
    cartitem_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = CartItem
        fields = ['cartitem_id', 'product', 'product_detail', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    class Meta:
        model = Cart
        fields = ["id", "created_at", "owner", "items"]
        read_only_fields = ['owner']