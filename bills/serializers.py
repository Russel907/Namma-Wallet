from rest_framework import serializers
from .models import Bill, Recharge

class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = ['id', 'bill_type', 'biller_name', 'consumer_number', 'amount', 'due_date', 'status', 'created_at']

class RechargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recharge
        fields = ['id', 'recharge_type', 'operator_name', 'mobile_number', 'amount', 'plan_description', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']