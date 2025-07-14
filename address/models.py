from django.db import models
from django.contrib.auth.models import User
from .constants import *

class Address(models.Model):
    ADDRESS_TYPE_CHOICES = [
        (ADDRESS_SHIPPING, 'Shipping'),
        (ADDRESS_BILLING, 'Billing'),
    ]

    user = models.ForeignKey(User, related_name='addresses', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=10, help_text='Number and 10 digits')
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6, help_text='Number and 6 digits')
    country = models.CharField(max_length=100, default='India')
    is_default = models.BooleanField(default=False)
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES, default=ADDRESS_SHIPPING)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', '-updated_at']

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(
                user=self.user,
                address_type=self.address_type,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} - {self.city} ({self.address_type})"