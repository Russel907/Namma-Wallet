from rest_framework import serializers
from .models import Ticket

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'ticket_type', 'from_location', 'to_location', 'travel_date', 'amount', 'status', 'created_at']