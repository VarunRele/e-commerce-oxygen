from rest_framework import serializers
from .models import Product, ProductImage

class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True, read_only=True)
    class Meta:
        model = ProductImage
        fields = ['image']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    product_id = serializers.IntegerField(source='id', read_only=True)
    class Meta:
        model = Product
        fields = [
            "product_id",
            "title",
            "description",
            "price",
            "images"
        ]
        read_only_fields = ["title", "description", "price", "images"]