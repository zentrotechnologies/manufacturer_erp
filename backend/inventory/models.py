from django.db import models
# Create your models here.
from helpers.models import TrackingModel
from django.conf import settings
from datetime import datetime, timedelta
from django.db.models.deletion import CASCADE
from Masters.models import *
from Purchase.models import *
from Sales.models import *
# Create your models here.
class RawInventory(TrackingModel):
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.PROTECT)
    quantity = models.FloatField()
class ProductionInventory(TrackingModel):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.FloatField()
class RawMaterialStockLedger(TrackingModel):
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.PROTECT)

    purchase_invoice = models.ForeignKey(
        PurchaseInvoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Used when stock is consumed in production"
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=[('IN', 'IN'), ('OUT', 'OUT')]
    )

    quantity = models.FloatField()
    rate_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    balance_quantity = models.FloatField()

    remarks = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.raw_material.name} | {self.transaction_type} | {self.quantity}"

class FinishedGoodsStockLedger(TrackingModel):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    sales_invoice = models.ForeignKey(
        SalesInvoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    transaction_type = models.CharField(
        max_length=10,
        choices=[('IN','IN'), ('OUT','OUT')]
    )
    quantity = models.FloatField()
    balance_quantity = models.FloatField()
    remarks = models.TextField(blank=True, null=True)


    
