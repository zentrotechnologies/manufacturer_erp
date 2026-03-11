from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from django.db import transaction
from django.db.models import Sum
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.db.models import Q
from .models import *
from .serializers import *
from Masters.models import *
from inventory.models import *
from User.common import *
from openpyxl import Workbook
from django.http import HttpResponse


def get_current_wip(product, machine):

    entries = ProductionEntry.objects.filter(
        product=product,
        machine=machine,
        isActive=True
    )

    total_added = entries.aggregate(
        total=Sum('batch__batch_weight_kg')
    )['total'] or 0

    total_consumed = entries.aggregate(
        total=Sum('finished_qty')
    )['total'] or 0

    return Decimal(total_added) - Decimal(total_consumed)

class CreateProductionEntryAPI(GenericAPIView):

    @transaction.atomic
    def post(self, request):

        data = request.data

        product = Product.objects.select_for_update().get(id=data['product'])
        batch = BatchMaster.objects.get(id=data['batch'])
        machine = Machine.objects.get(id=data['machine'])
        mould = Mould.objects.get(id=data['mould'])

        batches_made = int(data.get('batches_made', 0))
        finished_qty = int(data.get('finished_qty', 0))
        rejected_qty = int(data.get('rejected_qty', 0))

        if finished_qty <= 0:
            return Response({
                "response": {
                    "n": 0,
                    "msg": "Finished quantity must be greater than zero",
                    "status": "error"
                }
            })

        accepted_qty = finished_qty - rejected_qty

        # ===============================
        # STEP 1: WIP VALIDATION
        # ===============================

        current_wip = get_current_wip(product, machine)

        wip_added = batch.batch_weight_kg * Decimal(batches_made)
        wip_consumed = Decimal(finished_qty) * batch.kg_per_piece

        available_wip = current_wip + wip_added

        if wip_consumed > available_wip:
            return Response({
                "response": {
                    "n": 0,
                    "msg": "Not enough WIP available for this production",
                    "status": "error"
                }
            })

        # ===============================
        # STEP 2: CREATE PRODUCTION ENTRY
        # ===============================

        pe = ProductionEntry.objects.create(
            production_date=data['production_date'],
            shift=data['shift'],
            machine=machine,
            mould=mould,
            product=product,
            batch=batch,
            batches_made=batches_made,
            finished_qty=finished_qty,
            rejected_qty=rejected_qty,
            remarks=data.get('remarks')
        )

        # ===============================
        # STEP 3: RAW MATERIAL DEDUCTION
        # ===============================

        batch_materials = BatchRawMaterial.objects.filter(batch=batch)

        # total rubber / compound used
        total_material_used = Decimal(accepted_qty) * batch.kg_per_piece

        for rm in batch_materials:

            # material ratio inside batch
            ratio = rm.quantity_kg_per_batch / batch.batch_weight_kg

            qty_needed = ratio * total_material_used

            last_stock = RawMaterialStockLedger.objects.filter(
                raw_material=rm.raw_material
            ).order_by('-id').select_for_update().first()

            available = Decimal(last_stock.balance_quantity) if last_stock else Decimal('0')

            if available < qty_needed:
                raise ValidationError(
                    f"Insufficient stock for {rm.raw_material.name}"
                )

            rate = rm.rate_per_kg
            value = qty_needed * rate

            RawMaterialStockLedger.objects.create(
                raw_material=rm.raw_material,
                transaction_type='OUT',
                quantity=qty_needed,
                rate_per_unit=rate,
                balance_quantity=available - qty_needed,
                remarks=f"Production Entry #{pe.id}"
            )

            ProductionRawMaterialConsumption.objects.create(
                production_entry=pe,
                raw_material=rm.raw_material,
                quantity_consumed=qty_needed,
                rate_per_unit=rate,
                value_consumed=value
            )

        # ===============================
        # STEP 4: FINISHED GOODS INVENTORY
        # ===============================

        fg_stock = ProductionInventory.objects.select_for_update().filter(
            product=product
        ).first()

        if fg_stock:
            fg_stock.quantity += accepted_qty
            fg_stock.save()
        else:
            ProductionInventory.objects.create(
                product=product,
                quantity=accepted_qty
            )

        return Response({
            "data": {"production_entry_id": pe.id},
            "response": {
                "n": 1,
                "msg": "Production entry created successfully",
                "status": "success"
            }
        })   
            
class ProductionEntryListAPI(GenericAPIView):
    pagination_class = CustomPagination

    def post(self, request):

        search = request.data.get('searchtext')

        qs = ProductionEntry.objects.filter(
            isActive=True
        ).select_related('machine', 'product').order_by('-id')

        if search:
            qs = qs.filter(
                Q(product__name__icontains=search) |
                Q(machine__machine_code__icontains=search)
            )

        page = self.paginate_queryset(qs)

        data = []
        for p in page:
            data.append({
                "id": p.id,
                "production_date": p.production_date,
                "shift": p.shift,
                "machine": p.machine.machine_code,
                "product": p.product.name,
                "batch": p.batch.batch_name,
                "batches_made": p.batches_made,
                "finished_qty": p.finished_qty,
                "rejected_qty": p.rejected_qty,
                "accepted_qty": p.accepted_qty,
                "variance_percent": round(p.variance_percent, 2)
            })

        return self.get_paginated_response(data)
    
class GetProductionEntryByIdAPI(GenericAPIView):

    def post(self, request):

        entry_id = request.data.get('id')

        pe = ProductionEntry.objects.filter(
            id=entry_id,
            isActive=True
        ).select_related(
            'machine', 'mould', 'product', 'batch'
        ).first()

        if not pe:
            return Response({
                "response": {
                    "n": 0,
                    "msg": "Production entry not found",
                    "status": "error"
                }
            })

        return Response({
            "data": {
                "production_date": pe.production_date,
                "shift": pe.shift,
                "machine": pe.machine.machine_code,
                "mould": pe.mould.mould_code,
                "product": pe.product.name,
                "batch": pe.batch.batch_name,
                "batches_made": pe.batches_made,
                "finished_qty": pe.finished_qty,
                "rejected_qty": pe.rejected_qty,
                "accepted_qty": pe.accepted_qty,
                "variance_percent": round(pe.variance_percent, 2),
                "consumptions": [
                    {
                        "raw_material": c.raw_material.name,
                        "quantity": c.quantity_consumed,
                        "rate": c.rate_per_unit,
                        "value": c.value_consumed
                    }
                    for c in pe.consumptions.all()
                ]
            },
            "response": {
                "n": 1,
                "msg": "Production entry fetched successfully",
                "status": "success"
            }
        })

class DailyProductionReportAPI(GenericAPIView):

    def post(self, request):

        report_date = request.data.get('date')

        if not report_date:
            return Response({
                "data": [],
                "response": {
                    "n": 0,
                    "msg": "Report date is required",
                    "status": "error"
                }
            })

        qs = ProductionEntry.objects.filter(
            production_date=report_date,
            isActive=True
        ).select_related('machine', 'mould', 'product', 'batch')

        report = []

        for pe in qs:

            consumptions = pe.consumptions.all()

            total_material_cost = sum(
                c.value_consumed for c in consumptions
            )

            accepted_qty = pe.accepted_qty

            cost_per_piece = (
                total_material_cost / accepted_qty
                if accepted_qty > 0 else 0
            )

            report.append({
                "date": pe.production_date,
                "shift": pe.shift,
                "machine": pe.machine.machine_code,
                "product": pe.product.name,
                "batch": pe.batch.batch_name,
                "batches_made": pe.batches_made,
                "finished_qty": pe.finished_qty,
                "rejected_qty": pe.rejected_qty,
                "accepted_qty": accepted_qty,
                "variance_percent": round(pe.variance_percent, 2),
                "running_cavity": pe.mould.running_cavity,
                "total_cavity": pe.mould.total_cavity,
                "materials": [
                    {
                        "raw_material": c.raw_material.name,
                        "quantity": float(c.quantity_consumed),
                        "rate": float(c.rate_per_unit),
                        "value": float(c.value_consumed)
                    }
                    for c in consumptions
                ],
                "total_material_cost": float(round(total_material_cost, 2)),
                "cost_per_piece": float(round(cost_per_piece, 2))
            })

        return Response({
            "data": report,
            "response": {
                "n": 1,
                "msg": "Daily production report",
                "status": "success"
            }
        })

def export_daily_production_report_excel(request):

    report_date = request.GET.get('date')

    if not report_date:
        return HttpResponse("Date is required", status=400)

    qs = ProductionEntry.objects.filter(
        production_date=report_date,
        isActive=True
    ).select_related('machine', 'mould', 'product', 'batch')

    wb = Workbook()
    ws = wb.active
    ws.title = "Daily Production Report"

    headers = [
        "Shift",
        "Machine",
        "Product",
        "Batch",
        "Batches Made",
        "Finished Qty",
        "Rejected Qty",
        "Accepted Qty",
        "Variance %",
        "Running Cavity",
        "Total Cavity",
        "Total Material Cost",
        "Cost Per Piece"
    ]

    ws.append(headers)

    grand_material_cost = 0
    grand_accepted_qty = 0

    for pe in qs:

        total_material_cost = sum(
            c.value_consumed for c in pe.consumptions.all()
        )

        accepted_qty = pe.accepted_qty

        cost_per_piece = (
            total_material_cost / accepted_qty
            if accepted_qty > 0 else 0
        )

        ws.append([
            pe.shift,
            pe.machine.machine_code,
            pe.product.name,
            pe.batch.batch_name,
            pe.batches_made,
            pe.finished_qty,
            pe.rejected_qty,
            accepted_qty,
            round(pe.variance_percent, 2),
            pe.mould.running_cavity,
            pe.mould.total_cavity,
            float(round(total_material_cost, 2)),
            float(round(cost_per_piece, 2))
        ])

        grand_material_cost += total_material_cost
        grand_accepted_qty += accepted_qty

    ws.append([
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "TOTAL",
        "",
        "",
        "",
        float(round(grand_material_cost, 2)),
        float(round(
            (grand_material_cost / grand_accepted_qty)
            if grand_accepted_qty else 0, 2))
    ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response["Content-Disposition"] = (
        f"attachment; filename=Daily_Production_Report_{report_date}.xlsx"
    )

    wb.save(response)
    return response


class BatchListAPI(GenericAPIView):

    def post(self, request):

        qs = BatchMaster.objects.filter(
            isActive=True,
        ).select_related('product').order_by('-id')

        data = []

        for b in qs:
            data.append({
                "id": b.id,
                "batch_name": b.batch_name,
                "product": b.product.name,
                "batch_weight_kg": float(b.batch_weight_kg),
                "standard_output_qty": b.standard_output_qty
            })

        return Response({
            "data": data,
            "response": {
                "n": 1,
                "msg": "Batch list fetched successfully",
                "status": "success"
            }
        })
        
        
class batch_list_pagination_api(GenericAPIView):

    pagination_class = CustomPagination

    def post(self, request):

        search = request.data.get('searchtext')

        qs = BatchMaster.objects.filter(
            isActive=True,
            isDeleted=False
        ).select_related('product').order_by('-id')

        if search:
            qs = qs.filter(
                Q(batch_name__icontains=search) |
                Q(product__name__icontains=search)
            )

        page = self.paginate_queryset(qs)

        serializer = BatchSerializer(page, many=True)

        return self.get_paginated_response(serializer.data) 
        
        
class add_new_batch(GenericAPIView):

    @transaction.atomic
    def post(self, request):

        data = request.data

        if BatchMaster.objects.filter(
            batch_name=data.get('batch_name'),
            product=data.get('product'),
            isActive=True
        ).exists():

            return Response({
                "data": [],
                "response": {
                    "n": 0,
                    "msg": "Batch already exists for this product",
                    "status": "error"
                }
            })

        serializer = BatchSerializer(data=data)

        if serializer.is_valid():

            serializer.save(isActive=True)

            return Response({
                "data": serializer.data,
                "response": {
                    "n": 1,
                    "msg": "Batch created successfully",
                    "status": "success"
                }
            })

        first_key, first_value = next(iter(serializer.errors.items()))

        return Response({
            "data": serializer.errors,
            "response": {
                "n": 0,
                "msg": f"{first_key} : {first_value[0]}",
                "status": "error"
            }
        })
        
class batch_list(GenericAPIView):

    serializer_class = BatchSerializer

    def post(self, request):

        batches = BatchMaster.objects.filter(
            isActive=True,
            isDeleted=False
        )

        serializer = self.get_serializer(batches, many=True)

        return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "Batch list fetched successfully",
                "status": "success"
            }
        })
        
class get_batch_by_id(GenericAPIView):

    def post(self, request):

        batch_id = request.data.get('id')

        batch = BatchMaster.objects.filter(
            id=batch_id,
            isActive=True,
            isDeleted=False
        ).first()

        if not batch:

            return Response({
                "data": [],
                "response": {
                    "n": 0,
                    "msg": "Batch not found",
                    "status": "error"
                }
            })

        return Response({
            "data": BatchSerializer(batch).data,
            "response": {
                "n": 1,
                "msg": "Batch fetched successfully",
                "status": "success"
            }
        })
        
class update_batch(GenericAPIView):

    @transaction.atomic
    def post(self, request):

        batch_id = request.data.get('id')

        batch = BatchMaster.objects.filter(
            id=batch_id,
            isActive=True,
            isDeleted=False
        ).first()

        if not batch:
            return Response({
                "data": [],
                "response": {
                    "n": 0,
                    "msg": "Batch not found",
                    "status": "error"
                }
            })

        serializer = BatchSerializer(
            batch,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            serializer.save()

            return Response({
                "data": serializer.data,
                "response": {
                    "n": 1,
                    "msg": "Batch updated successfully",
                    "status": "success"
                }
            })

        first_key, first_value = next(iter(serializer.errors.items()))

        return Response({
            "data": serializer.errors,
            "response": {
                "n": 0,
                "msg": f"{first_key} : {first_value[0]}",
                "status": "error"
            }
        })
        
class delete_batch(GenericAPIView):

    def post(self, request):

        batch_id = request.data.get('id')

        batch = BatchMaster.objects.filter(
            id=batch_id,
            isActive=True
        ).first()

        if not batch:

            return Response({
                "data": [],
                "response": {
                    "n": 0,
                    "msg": "Batch not found",
                    "status": "error"
                }
            })

        batch.isActive = False
        batch.isDeleted = True
        batch.save()

        return Response({
            "data": [],
            "response": {
                "n": 1,
                "msg": "Batch deleted successfully",
                "status": "success"
            }
        })
        
        
        
        
        
        
        
        
        
        
        
        
        