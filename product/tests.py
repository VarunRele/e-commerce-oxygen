from django.test import TestCase
from .models import Product

class ProductModelTest(TestCase):
    def test_create_product(self):
        product = Product.objects.create(
            title = "Test product",
            description = "A test product",
            price = 9.99
        )
        self.assertEqual(product.title, "Test product")
        self.assertEqual(product.price, 9.99)

    def test_required_fields(self):
        product = Product.objects.create(
            description = "Missing title",
            price = 9.99
        )
        with self.assertRaises(Exception):
            product.full_clean() 