from django.contrib import admin
from .models import Product, ProductImage

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["title", "description", "price"]

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    pass