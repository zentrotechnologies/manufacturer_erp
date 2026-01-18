from django.db import models
# Create your models here.
from helpers.models import TrackingModel
from django.conf import settings
from datetime import datetime, timedelta
from django.db.models.deletion import CASCADE
from Masters.models import *
from User.models import *
# Create your models here.
class SalesInvoice(TrackingModel):
    invoice_number = models.CharField(max_length=50, unique=True)
    invoice_date = models.DateField()

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)

    buyer_order_no = models.CharField(max_length=50, blank=True, null=True)
    buyer_order_date = models.DateField(blank=True, null=True)

    same_state = models.BooleanField(default=True)

    base_amount = models.DecimalField(max_digits=15, decimal_places=2)
    gst_amount = models.DecimalField(max_digits=15, decimal_places=2)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)

    payment_terms = models.CharField(max_length=50, default="30 Days")
    payment_status=models.CharField(max_length=50, default="Pending")
    def __str__(self):
        return self.invoice_number
class SalesInvoiceItem(TrackingModel):
    sales_invoice = models.ForeignKey(
        SalesInvoice,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    hsn_code = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.FloatField()
    rate_per_unit = models.DecimalField(max_digits=10, decimal_places=2)

    base_amount = models.DecimalField(max_digits=15, decimal_places=2)
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    gst_amount = models.DecimalField(max_digits=15, decimal_places=2)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
