from django.test import TestCase
from django.contrib.auth.models import User
from product.models import Product
from .models import Cart, CartItem
from rest_framework.test import APIClient
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist


class CartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.product = Product.objects.create(title='Test product', price=10.0)
        self.cart, created = Cart.objects.get_or_create(owner=self.user)

    def test_cart_creation(self):
        self.assertEqual(str(self.cart), "testuser's cart")

    def test_cartitem_creation(self):
        cart_item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        self.assertEqual(str(cart_item), "2 x Test product")


class CartViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.product = Product.objects.create(title='Test product', price=10.0)
        self.client = APIClient()
        self.client.login(username='testuser', password='pass')
        self.cart, created = Cart.objects.get_or_create(owner=self.user)

    def test_cart_list_authenticated(self):
        response = self.client.get('/api/cart/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_cart_item(self):
        response = self.client.post('/api/cart/add/', {'product': self.product.id, 'quantity': 1})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_increment_cart_item(self):
        cart_item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)
        response = self.client.put(f'/api/cart/increment/{cart_item.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 2)

    def test_decrement_cart_item(self):
        cart_item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        response = self.client.put(f'/api/cart/decrement/{cart_item.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 1)

    def test_decrement_cart_item_to_zero(self):
        cart_item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)
        response = self.client.put(f'/api/cart/decrement/{cart_item.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(ObjectDoesNotExist):
            cart_item.refresh_from_db()