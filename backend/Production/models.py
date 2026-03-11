from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum
from decimal import Decimal
from helpers.models import TrackingModel
from Masters.models import Product, RawMaterial, Machine, Mould


# =====================================================
# BATCH MASTER (Formula Engine)
# =====================================================

class BatchMaster(TrackingModel):
    batch_name = models.CharField(max_length=100)

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='batches'
    )

    batch_weight_kg = models.DecimalField(max_digits=12, decimal_places=3)
    standard_output_qty = models.PositiveIntegerField()



    def __str__(self):
        return f"{self.product.name} - {self.batch_name}"

    @property
    def kg_per_piece(self):
        if self.standard_output_qty == 0:
            return Decimal('0')
        return self.batch_weight_kg / Decimal(self.standard_output_qty)


# =====================================================
# BATCH RAW MATERIAL (Child Table)
# =====================================================

class BatchRawMaterial(TrackingModel):
    batch = models.ForeignKey(
        BatchMaster,
        on_delete=models.CASCADE,
        related_name='raw_materials'
    )

    raw_material = models.ForeignKey(
        RawMaterial,
        on_delete=models.PROTECT
    )
    material_type = models.CharField(
        max_length=50,
        choices=[
            ('RUBBER','Rubber'),
            ('METAL','Metal'),
            ('INSERT','Insert'),
            ('CHEMICAL','Chemical')
        ],
        default='RUBBER'
    )
    quantity_kg_per_batch = models.DecimalField(max_digits=12, decimal_places=3)
    rate_per_kg = models.DecimalField(max_digits=12, decimal_places=2)


    def total_cost(self):
        return self.quantity_kg_per_batch * self.rate_per_kg

    def __str__(self):
        return f"{self.raw_material.name} - {self.batch.batch_name}"


# =====================================================
# PRODUCTION ENTRY
# =====================================================

class ProductionEntry(TrackingModel):

    SHIFT_CHOICES = (
        ('SHIFT-1', 'Shift 1'),
        ('SHIFT-2', 'Shift 2'),
        ('SHIFT-3', 'Shift 3'),
    )

    production_date = models.DateField()
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES)

    machine = models.ForeignKey(
        Machine,
        on_delete=models.PROTECT
    )

    mould = models.ForeignKey(
        Mould,
        on_delete=models.PROTECT
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )
    operator_name = models.CharField(max_length=100, blank=True, null=True)

    running_cavity = models.PositiveIntegerField(null=True, blank=True)
    batch = models.ForeignKey(
        BatchMaster,
        on_delete=models.PROTECT
    )

    # Mixing
    batches_made = models.PositiveIntegerField(default=0)

    # Output
    finished_qty = models.PositiveIntegerField()
    rejected_qty = models.PositiveIntegerField(default=0)

    remarks = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-production_date', '-id']
        indexes = [
            models.Index(fields=['product', 'machine']),
            models.Index(fields=['production_date']),
        ]

    def __str__(self):
        return f"{self.product.name} | {self.machine.machine_code} | {self.production_date}"

    # ===============================
    # VALIDATION
    # ===============================

    def clean(self):

        if self.batch.product != self.product:
            raise ValidationError("Selected batch does not belong to this product.")

        if self.rejected_qty > self.finished_qty:
            raise ValidationError("Rejected quantity cannot exceed finished quantity.")

    # ===============================
    # CALCULATED FIELDS
    # ===============================

    @property
    def accepted_qty(self):
        return self.finished_qty - self.rejected_qty

    @property
    def expected_qty(self):
        return self.batch.standard_output_qty * self.batches_made

    @property
    def variance_qty(self):
        return self.finished_qty - self.expected_qty

    @property
    def variance_percent(self):
        if self.expected_qty == 0:
            return 0
        return (self.variance_qty / self.expected_qty) * 100

    @property
    def wip_added_kg(self):
        return self.batch.batch_weight_kg * self.batches_made

    @property
    def wip_consumed_kg(self):
        return self.finished_qty * self.batch.kg_per_piece


# =====================================================
# RAW MATERIAL CONSUMPTION LOG
# =====================================================

class ProductionRawMaterialConsumption(TrackingModel):

    production_entry = models.ForeignKey(
        ProductionEntry,
        on_delete=models.CASCADE,
        related_name='consumptions'
    )

    raw_material = models.ForeignKey(
        RawMaterial,
        on_delete=models.PROTECT
    )
    material_type = models.CharField(
        max_length=50,
        choices=[
            ('RUBBER','Rubber'),
            ('METAL','Metal'),
            ('INSERT','Insert'),
            ('CHEMICAL','Chemical')
        ],
        default='RUBBER'
    )
    quantity_consumed = models.DecimalField(max_digits=15, decimal_places=3)
    rate_per_unit = models.DecimalField(max_digits=12, decimal_places=2)
    value_consumed = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        indexes = [
            models.Index(fields=['production_entry']),
        ]

    def __str__(self):
        return f"PE#{self.production_entry.id} - {self.raw_material.name}"