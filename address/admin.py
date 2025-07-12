from django.contrib import admin
from .models import Address
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'full_name', 'phone_number', 'address_type',
        'is_default', 'city', 'state', 'pincode', 'country', 'created_at'
    ]
    list_filter = ['address_type', 'is_default', 'state', 'country']
    search_fields = ['user__username', 'full_name', 'phone_number', 'city', 'pincode']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-is_default', '-updated_at']


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0


class CustomUserAdmin(UserAdmin):
    inlines = [AddressInline]

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)