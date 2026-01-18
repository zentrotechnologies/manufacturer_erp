# Sales/serializers.py
from rest_framework import serializers
from .models import SalesInvoice

class SalesInvoiceListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)

    class Meta:
        model = SalesInvoice
        fields = [
            'id',
            'invoice_number',
            'invoice_date',
            'customer_name',
            'base_amount',
            'gst_amount',
            'total_amount'
        ]
