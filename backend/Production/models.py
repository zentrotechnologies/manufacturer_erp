from django.db import models
# Create your models here.
from helpers.models import TrackingModel
from django.conf import settings
from datetime import datetime, timedelta
from django.db.models.deletion import CASCADE
from Masters.models import *
# Create your models here.
class ProductionEntry(TrackingModel):
    production_date = models.DateField()
    shift = models.CharField(
        max_length=20,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C')]
    )

    machine = models.ForeignKey(Machine, on_delete=models.PROTECT)
    mould = models.ForeignKey(Mould, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    operator_name = models.CharField(max_length=100, blank=True, null=True)

    planned_quantity = models.FloatField(default=0)
    produced_quantity = models.FloatField()
    rejected_quantity = models.FloatField(default=0)

    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.production_date} - {self.product.name}"
    
    
class ProductionRawMaterialConsumption(TrackingModel):
    production_entry = models.ForeignKey(
        ProductionEntry,
        on_delete=models.CASCADE
    )
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.PROTECT)
    quantity_consumed = models.FloatField()
    rate_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    value_consumed = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"{self.production_entry.id} - {self.raw_material.name}"
