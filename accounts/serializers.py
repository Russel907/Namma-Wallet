from rest_framework import serializers
from .models import User, Address, LinkedCard

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['mobile_number', 'username', 'first_name', 'last_name', 'email', 'is_mobile_verified']
        read_only_fields = ['mobile_number', 'is_mobile_verified']

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id',
            'address_type', 
            'full_address', 
            'city', 
            'pincode', 
            'is_default', 
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class LinkedCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkedCard
        fields = [
            'id',
            'card_holder_name',
            'last_four_digits',
            'card_type',
            'card_category',
            'expiry_month',
            'expiry_year',
            'is_default',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']