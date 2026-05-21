from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    mobile_number = models.CharField(max_length=15, unique=True)
    is_mobile_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'mobile_number'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.mobile_number

class OTP(models.Model):
    mobile_number = models.CharField(max_length=15)
    otp_code = models.CharField(max_length=20, default='mc_generated')
    provider_verification_id = models.CharField(max_length=100, null=True, blank=True)
    provider_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.mobile_number} - {self.otp_code}"

class Address(models.Model):
    ADDRESS_TYPES = [
        ('HOME', 'Home'),
        ('OFFICE', 'Office'),
        ('OTHER', 'Other'),
    ]
    
    # Which user this address belongs to
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='addresses'
    )
    
    # Type of address - Home, Office or Other
    address_type = models.CharField(
        max_length=10, 
        choices=ADDRESS_TYPES, 
        default='HOME'
    )
    
    # Full address details
    full_address = models.TextField()
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)
    
    # Is this the default address?
    is_default = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.mobile_number} - {self.address_type}"

class LinkedCard(models.Model):
    CARD_TYPES = [
        ('VISA', 'Visa'),
        ('MASTERCARD', 'Mastercard'),
        ('RUPAY', 'RuPay'),
        ('AMEX', 'American Express'),
    ]

    CARD_CATEGORIES = [
        ('DEBIT', 'Debit Card'),
        ('CREDIT', 'Credit Card'),
    ]

    # Which user this card belongs to
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='linked_cards'
    )

    # Card details — never store full number!
    card_holder_name = models.CharField(max_length=100)
    last_four_digits = models.CharField(max_length=4)
    card_type = models.CharField(max_length=15, choices=CARD_TYPES)
    card_category = models.CharField(max_length=10, choices=CARD_CATEGORIES)
    expiry_month = models.CharField(max_length=2)
    expiry_year = models.CharField(max_length=4)

    # Token from payment gateway — used instead of full card number
    gateway_token = models.CharField(max_length=255, blank=True, null=True)

    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.mobile_number} - {self.card_type} - {self.last_four_digits}"

class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ('CAR', 'Car'),
        ('BIKE', 'Bike'),
        ('AUTO', 'Auto'),
        ('OTHER', 'Other'),
    ]

    # Connect to user
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='vehicles'
    )

    # Vehicle details
    vehicle_name = models.CharField(max_length=100)
    vehicle_number = models.CharField(max_length=20)
    vehicle_type = models.CharField(
        max_length=10,
        choices=VEHICLE_TYPES,
        default='CAR'
    )
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.mobile_number} - {self.vehicle_type} - {self.vehicle_number}"