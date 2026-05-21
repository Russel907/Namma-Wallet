from django.db import models
from accounts.models import User

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('USED', 'Used'),
        ('EXPIRED', 'Expired'),
    ]

    TICKET_TYPES = [
        ('BUS', 'Bus'),
        ('METRO', 'Metro'),
        ('TRAIN', 'Train'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    ticket_type = models.CharField(max_length=10, choices=TICKET_TYPES)
    from_location = models.CharField(max_length=100)
    to_location = models.CharField(max_length=100)
    travel_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.mobile_number} - {self.ticket_type} - {self.status}"