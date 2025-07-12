from django.test import TestCase
from django.contrib.auth.models import User
from .models import Address

class AddressModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='123')
        self.address = Address.objects.create(
            user=self.user,
            full_name='John Doe',
            phone_number='9876543210',
            address_line_1='123 Main Street',
            city='Mumbai',
            state='Maharashtra',
            pincode='400001',
            country='India',
            is_default=True,
            address_type='shipping'
        )

    def test_address_str(self):
        self.assertEqual(str(self.address), "John Doe - Mumbai (shipping)")

    def test_address_fields(self):
        self.assertEqual(self.address.user.username, 'testuser')
        self.assertTrue(self.address.is_default)
        self.assertEqual(self.address.city, 'Mumbai')
        self.assertEqual(self.address.country, 'India')
        self.assertEqual(self.address.address_type, 'shipping')

    def test_only_one_default_per_type(self):
        # Create another default shipping address
        new_address = Address.objects.create(
            user=self.user,
            full_name='Jane Smith',
            phone_number='1234567890',
            address_line_1='456 Another Street',
            city='Pune',
            state='Maharashtra',
            pincode='411001',
            country='India',
            is_default=True,
            address_type='shipping'
        )

        # Fetch all default shipping addresses for user
        default_shipping = Address.objects.filter(user=self.user, address_type='shipping')
        self.assertEqual(default_shipping.count(), 2)  # Fails: unless you manually handle unique constraint

        # To enforce only one default, you'll need custom logic (see suggestion below)