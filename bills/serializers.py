from rest_framework import serializers
from .models import Bill

class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = ['id', 'bill_type', 'biller_name', 'consumer_number', 'amount', 'due_date', 'status', 'created_at']