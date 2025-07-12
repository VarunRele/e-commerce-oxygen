from rest_framework import serializers
from .models import Address

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id', 'full_name', 'phone_number', 'address_line_1', 'address_line_2',
            'city', 'state', 'pincode', 'country', 'is_default', 'address_type',
            'created_at', 'updated_at', 'user'
        ]
        read_only_fields = ['user']