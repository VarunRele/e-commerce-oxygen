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

    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")
        if len(value) != 10:
            raise serializers.ValidationError("Phone number must be exactly 10 digits.")
        return value

    def validate_pincode(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Pincode must contain only digits.")
        if len(value) != 6:
            raise serializers.ValidationError("Pincode must be exactly 6 digits.")
        return value