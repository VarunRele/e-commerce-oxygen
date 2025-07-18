from django.test import TestCase
from django.contrib.auth.models import User
from .models import Order, OrderItem
from cart.models import Cart, CartItem
from product.models import Product
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework import status
from address.models import Address
from .permission import IsOwnerOrAdmin


class OrderViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.client = APIClient()
        self.client.login(username="testuser", password="pass")
        self.cart, created = Cart.objects.get_or_create(owner=self.user)
        self.product1 = Product.objects.create(title='Product 1', price=20.0)
        self.product2 = Product.objects.create(title='Product 2', price=30.0)
        self.address = Address.objects.create(
            user = self.user,
            full_name = 'Test user',
            phone_number = '38353043',
            address_line_1 = 'Test address',
            city = 'LA',
            state = 'WA',
            pincode = '4853343',
        )
        
    def test_create_order_when_cart_not_empty_then_empty_the_cart(self):
        CartItem.objects.create(cart=self.cart, product=self.product1, quantity=1)
        CartItem.objects.create(cart=self.cart, product=self.product2, quantity=3)
        self.client.post("/api/order/", data = {'shipping_address': self.address.pk})
        cart_count = self.cart.items.count()
        self.assertEqual(cart_count, 0)

    def test_dont_create_order_when_cart_empty(self):
        cart_count = self.cart.items.count()
        self.assertEqual(cart_count, 0)
        response = self.client.post("/api/order/", data = {'shipping_address': self.address.pk})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_when_cart_not_empty(self):
        CartItem.objects.create(cart=self.cart, product=self.product1, quantity=1)
        CartItem.objects.create(cart=self.cart, product=self.product2, quantity=3)
        response = self.client.post("/api/order/", data = {'shipping_address': self.address.pk})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order = Order.objects.prefetch_related('items').filter(user=self.user).get(id=response.json()['order_id'])
        self.assertEqual(order.items.count(), 2)

    def test_cant_see_others_order(self):
        CartItem.objects.create(cart=self.cart, product=self.product1, quantity=1)
        CartItem.objects.create(cart=self.cart, product=self.product2, quantity=3)
        order_response = self.client.post("/api/order/", data = {'shipping_address': self.address.pk})
        order_id = order_response.json().get('order_id')
        new_user = User.objects.create_user(username='new', password='pass')
        client = APIClient()
        response = client.get(f'/api/order/{order_id}/')
        self.assertIn(response.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])

    def test_cancel_order(self):
        order = Order.objects.create(user=self.user, payment_status='pending', delivery_status='processing')
        OrderItem.objects.create(order=order, product=self.product1, quantity=2, price=20.0) 
        response = self.client.post(f'/api/order/cancel/{order.pk}/')
        order.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(order.delivery_status, 'cancelled')


class IsOwnerOrAdminPermissionTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

        self.owner = User.objects.create_user(username='owner', password='pass')
        self.admin = User.objects.create_superuser(username='admin', password='pass', email='admin@email.com')
        self.stranger = User.objects.create_user(username='stranger', password='pass')
        self.client = APIClient()

        self.order = Order.objects.create(
            user=self.owner 
            )

    def test_owner_has_permission(self):
        request = self.factory.get(f'/api/order/{self.order.pk}/')        
        request.user = self.owner
        permission = IsOwnerOrAdmin()
        self.assertTrue(permission.has_object_permission(request, None, self.order))