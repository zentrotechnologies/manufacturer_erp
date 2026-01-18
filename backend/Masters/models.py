from django.db import models
# Create your models here.
from helpers.models import TrackingModel
from django.conf import settings
from datetime import datetime, timedelta
from django.db.models.deletion import CASCADE
# Create your models here.

class Vendor(TrackingModel):
    name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    gstin= models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name
    
class RawMaterial(TrackingModel):
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=20)  # KG, TON, NOS
    hsn_code = models.CharField(max_length=50, blank=True, null=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    
    def __str__(self):
        return self.name

class Machine(TrackingModel):
    machine_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.machine_code

class Mould(TrackingModel):
    mould_code = models.CharField(max_length=50, unique=True)
    machine = models.ForeignKey(Machine, on_delete=models.PROTECT)
    total_cavity = models.PositiveIntegerField()
    running_cavity = models.PositiveIntegerField()

    def __str__(self):
        return self.mould_code
    
class Product(TrackingModel):
    part_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    mould = models.ForeignKey(Mould, on_delete=models.PROTECT)
    hsn_code = models.CharField(max_length=50, blank=True, null=True)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    
    
    def __str__(self):
        return self.name
    
    
    
class ProductConfiguration(TrackingModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='bom_items'
    )
    raw_material = models.ForeignKey(
        RawMaterial,
        on_delete=models.PROTECT,
        related_name='used_in_products'
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        help_text="Quantity of raw material required per product"
    )
    unit = models.CharField(
        max_length=20,
        help_text="KG, NOS, TON etc"
    )
    wastage_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    class Meta:
        db_table = "product_configuration"
        unique_together = ('product', 'raw_material')

    def __str__(self):
        return f"{self.product.name} - {self.raw_material.name}"
