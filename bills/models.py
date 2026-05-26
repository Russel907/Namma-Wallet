from django.db import models
from accounts.models import User

class Bill(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
    ]

    BILL_TYPES = [
        ('ELECTRICITY', 'Electricity'),
        ('WATER', 'Water'),
        ('GAS', 'Gas'),
        ('MOBILE', 'Mobile'),
        ('DTH', 'DTH'),
        ('FASTAG', 'Fastag'),
        ('BROADBAND', 'Broadband'),
        ('CREDIT_CARD', 'Credit Card'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bills')
    bill_type = models.CharField(max_length=20, choices=BILL_TYPES)
    biller_name = models.CharField(max_length=100)
    consumer_number = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.mobile_number} - {self.bill_type} - {self.status}"

class Recharge(models.Model):
    RECHARGE_TYPES = [
        ('MOBILE_PREPAID', 'Mobile Prepaid'),
        ('MOBILE_POSTPAID', 'Mobile Postpaid'),
        ('DTH', 'DTH'),
        ('FASTAG', 'FASTag'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recharges'
    )
    recharge_type = models.CharField(max_length=20, choices=RECHARGE_TYPES)
    operator_name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    plan_description = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.mobile_number} - {self.recharge_type} - ₹{self.amount}"