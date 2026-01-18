from django.db import models
# Create your models here.
from helpers.models import TrackingModel
from django.conf import settings
from datetime import datetime, timedelta
from django.db.models.deletion import CASCADE
from Masters.models import *

# Create your models here.

class PurchaseInvoice(TrackingModel):
    invoice_number = models.CharField(max_length=50, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT)
    invoice_date = models.DateField()
    base_amount = models.DecimalField(max_digits=15, decimal_places=2)
    gst_amount = models.DecimalField(max_digits=15, decimal_places=2)
    same_state = models.BooleanField(default=True)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Paid', 'Paid')], default='Pending')
    total_quantity = models.FloatField()
    total_weight = models.FloatField()
    
    
    def __str__(self):
        return self.invoice_number
    
class PurchaseItem(TrackingModel):
    purchase_invoice = models.ForeignKey(PurchaseInvoice, on_delete=models.CASCADE)
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.PROTECT)
    hsn_code = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.FloatField()
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    rate_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    base_amount = models.DecimalField(max_digits=15, decimal_places=2)
    gst_amount = models.DecimalField(max_digits=15, decimal_places=2)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    def __str__(self):
        return f"{self.purchase_invoice.invoice_number} - {self.raw_material.name}"
    
    
    