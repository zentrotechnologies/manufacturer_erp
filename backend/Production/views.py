from django.shortcuts import render

# Create your views here.from rest_framework.response import Response
from rest_framework.authentication import (BaseAuthentication,
                                           get_authorization_header)
from rest_framework import permissions
from rest_framework.response import Response
import json
from rest_framework.generics import GenericAPIView
from django.contrib.auth import authenticate
from .models import *
from .serializers import *
from User.jwt import userJWTAuthentication
from django.template.loader import get_template, render_to_string
from django.core.mail import EmailMessage
from manufacturer_erp.settings import EMAIL_HOST_USER
from User.common import CustomPagination
from django.db.models import Q

# Create your views here.
from django.db import transaction
from inventory.models import *
from django.db.models import Sum
from django.db.models import F



from decimal import Decimal, ROUND_HALF_UP

class create_production_entry(GenericAPIView):

    @transaction.atomic
    def post(self, request):
        data = request.data

        produced_qty = Decimal(data.get('produced_quantity', '0'))
        rejected_qty = Decimal(data.get('rejected_quantity', '0'))
        accepted_qty = produced_qty - rejected_qty

        if accepted_qty <= 0:
            return Response({
                "data": [],
                "response": {
                    "n": 0,
                    "msg": "Accepted quantity must be greater than zero",
                    "status": "error"
                }
            })

        product = Product.objects.select_for_update().get(id=data['product'])
        mould = Mould.objects.get(id=data['mould'])

        # ---- CREATE PRODUCTION ENTRY ----
        pe = ProductionEntry.objects.create(
            production_date=data['production_date'],
            shift=data['shift'],
            machine_id=data['machine'],
            mould=mould,
            product=product,
            operator_name=data.get('operator_name'),
            planned_quantity=Decimal(data.get('planned_quantity', '0')),
            produced_quantity=produced_qty,
            rejected_quantity=rejected_qty,
            remarks=data.get('remarks')
        )

        # ---- RAW MATERIAL CONSUMPTION (BOM) ----
        bom_items = ProductConfiguration.objects.select_related(
            'raw_material'
        ).filter(product=product)

        for bom in bom_items:
            qty_needed = (accepted_qty * Decimal(bom.quantity)).quantize(
                Decimal('0.000'), ROUND_HALF_UP
            )

            last_stock = RawMaterialStockLedger.objects.filter(
                raw_material=bom.raw_material
            ).order_by('-id').select_for_update().first()

            available = (
                Decimal(last_stock.balance_quantity)
                if last_stock else Decimal('0')
            )

            if available < qty_needed:
                return Response({
                    "data": {
                        "raw_material": bom.raw_material.name,
                        "available_qty": round(available, 3),
                        "required_qty": round(qty_needed, 3)
                    },
                    "response": {
                        "n": 0,
                        "msg": (
                            f"Insufficient stock for {bom.raw_material.name}. "
                            f"Available: {available}, Required: {qty_needed}"
                        ),
                        "status": "error"
                    }
                })

            rate = Decimal(bom.raw_material.price_per_unit)

            value = (qty_needed * rate).quantize(
                Decimal('0.01'), ROUND_HALF_UP
            )

            # ---- RAW MATERIAL LEDGER (OUT) ----
            RawMaterialStockLedger.objects.create(
                raw_material=bom.raw_material,
                transaction_type='OUT',
                quantity=qty_needed,
                rate_per_unit=rate,
                balance_quantity=available - qty_needed,
                remarks=f"Production Entry #{pe.id}"
            )

            # ---- CONSUMPTION LOG ----
            ProductionRawMaterialConsumption.objects.create(
                production_entry=pe,
                raw_material=bom.raw_material,
                quantity_consumed=qty_needed,
                rate_per_unit=rate,
                value_consumed=value
            )

        # ---- FINISHED GOODS INVENTORY (IN) ----
        fg_stock = ProductionInventory.objects.select_for_update().filter(
            product=product
        ).first()

        if fg_stock:
            fg_stock.quantity = float(fg_stock.quantity) + float(accepted_qty)
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

class production_entry_list_pagination_api(GenericAPIView):
    pagination_class = CustomPagination

    def post(self, request):
        search = request.data.get('searchtext')

        qs = ProductionEntry.objects.filter(isActive=True).order_by('-id')

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
                "produced_quantity": p.produced_quantity,
                "rejected_quantity": p.rejected_quantity,
            })

        return self.get_paginated_response(data)


class get_production_entry_by_id(GenericAPIView):

    def post(self, request):
        entry_id = request.data.get('id')

        pe = ProductionEntry.objects.filter(
            id=entry_id,
            isActive=True
        ).first()

        if not pe:
            return Response({
                "data": [],
                "response": {
                    "n": 0,
                    "msg": "Production entry not found",
                    "status": "error"
                }
            })

        consumptions = ProductionRawMaterialConsumption.objects.filter(
            production_entry=pe
        )

        return Response({
    "data": {
        "entry": {
            "production_date": pe.production_date,
            "shift": pe.shift,
            "machine": pe.machine.machine_code,
            "mould": pe.mould.mould_code,
            "product": pe.product.name,
            "produced_quantity": pe.produced_quantity,
            "rejected_quantity": pe.rejected_quantity,
            "operator_name": pe.operator_name,
            "remarks": pe.remarks,
        },
        "consumptions": [
            {
                "raw_material_name": c.raw_material.name,
                "raw_material_unit": c.raw_material.unit,
                "quantity_consumed": c.quantity_consumed,
                "rate_per_unit": c.rate_per_unit,
                "value_consumed": c.value_consumed
            }
            for c in consumptions
        ]
    },
    "response": {
        "n": 1,
        "msg": "Production entry fetched",
        "status": "success"
    }
})



class daily_production_report_api(GenericAPIView):

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
        )

        report = []

        for pe in qs:
            consumptions = ProductionRawMaterialConsumption.objects.filter(
                production_entry=pe
            )

            total_value = sum(
                float(c.value_consumed) for c in consumptions
            )

            net_qty = pe.produced_quantity - pe.rejected_quantity
            cost_per_piece = (
                total_value / net_qty if net_qty > 0 else 0
            )

            report.append({
                "date": pe.production_date,
                "shift": pe.shift,
                "machine": pe.machine.machine_code,
                "product": pe.product.name,
                "running_cavity": pe.mould.running_cavity,
                "total_cavity": pe.mould.total_cavity,
                "planned_qty": pe.planned_quantity,
                "produced_qty": pe.produced_quantity,
                "rejected_qty": pe.rejected_quantity,
                "net_qty": net_qty,
                "rejection_percent": round(
                    (pe.rejected_quantity / pe.produced_quantity) * 100, 2
                ) if pe.produced_quantity else 0,
                "materials": [
                    {
                        "raw_material": c.raw_material.name,
                        "qty": c.quantity_consumed,
                        "rate": c.rate_per_unit,
                        "value": c.value_consumed
                    } for c in consumptions
                ],
                "total_material_cost": round(total_value, 2),
                "cost_per_piece": round(cost_per_piece, 2)
            })

        return Response({
            "data": report,
            "response": {
                "n": 1,
                "msg": "Daily production report",
                "status": "success"
            }
        })

from openpyxl import Workbook
from django.http import HttpResponse
from datetime import datetime

# def export_daily_production_report_excel(request):
#     report_date = request.GET.get('date')

#     if not report_date:
#         return HttpResponse("Date is required", status=400)

#     qs = ProductionEntry.objects.filter(
#         production_date=report_date,
#         isActive=True
#     ).select_related(
#         'machine', 'mould', 'product'
#     )

#     wb = Workbook()
#     ws = wb.active
#     ws.title = "Daily Production Report"

#     # 🔹 HEADER
#     headers = [
#         "Date", "Shift", "Machine", "Product",
#         "Running Cavity", "Total Cavity",
#         "Planned Qty", "Produced Qty",
#         "Rejected Qty", "Net Qty",
#         "Raw Material", "Consumed Qty",
#         "Rate", "Consumed Value",
#         "Total Material Cost", "Cost / Piece"
#     ]
#     ws.append(headers)

#     # 🔹 DATA
#     for pe in qs:
#         consumptions = ProductionRawMaterialConsumption.objects.filter(
#             production_entry=pe
#         )

#         total_value = sum(
#             float(c.value_consumed) for c in consumptions
#         )

#         net_qty = pe.produced_quantity - pe.rejected_quantity
#         cost_per_piece = (
#             total_value / net_qty if net_qty > 0 else 0
#         )

#         if consumptions.exists():
#             for c in consumptions:
#                 ws.append([
#                     pe.production_date,
#                     pe.shift,
#                     pe.machine.machine_code,
#                     pe.product.name,
#                     pe.mould.running_cavity,
#                     pe.mould.total_cavity,
#                     pe.planned_quantity,
#                     pe.produced_quantity,
#                     pe.rejected_quantity,
#                     net_qty,
#                     c.raw_material.name,
#                     c.quantity_consumed,
#                     float(c.rate_per_unit),
#                     float(c.value_consumed),
#                     round(total_value, 2),
#                     round(cost_per_piece, 2),
#                 ])
#         else:
#             ws.append([
#                 pe.production_date,
#                 pe.shift,
#                 pe.machine.machine_code,
#                 pe.product.name,
#                 pe.mould.running_cavity,
#                 pe.mould.total_cavity,
#                 pe.planned_quantity,
#                 pe.produced_quantity,
#                 pe.rejected_quantity,
#                 net_qty,
#                 "-", 0, 0, 0,
#                 round(total_value, 2),
#                 round(cost_per_piece, 2),
#             ])

#     # 🔹 RESPONSE
#     response = HttpResponse(
#         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#     )
#     filename = f"Daily_Production_Report_{report_date}.xlsx"
#     response['Content-Disposition'] = f'attachment; filename={filename}'

#     wb.save(response)
#     return response




def export_daily_production_report_excel(request):
    report_date = request.GET.get('date')

    if not report_date:
        return HttpResponse("Date is required", status=400)

    qs = ProductionEntry.objects.filter(
        production_date=report_date,
        isActive=True
    ).select_related('machine', 'mould', 'product')

    wb = Workbook()
    ws = wb.active
    ws.title = "Daily Production Report"

    headers = [
        "Shift No","M/C No","Name","Part Name",
        "Running Cavity","Total Cavity",
        "Target","Actual","Sh Qty","Total Qty",
        "Rej (P)","Rej (QA)","Rej (FD)","Accep.",
        "RATE","Value","Rej Value","Rej%",
        "LOP","Ld Wt",
        "Rubber Cons. (KG)","C. Rate","Value Cons.",
        "Metal","Insert Val.","Total Cons Val","Cons. %"
    ]
    ws.append(headers)

    grand_value = 0
    grand_rej_value = 0
    grand_total_cons = 0

    for pe in qs:
        consumptions = ProductionRawMaterialConsumption.objects.filter(
            production_entry=pe
        )

        total_qty = pe.produced_quantity
        rej_p = pe.rejected_quantity
        rej_qa = 0
        rej_fd = 0

        total_rej = rej_p + rej_qa + rej_fd
        accepted = float(total_qty - total_rej)

        rate = float(pe.product.price_per_unit)
        value = accepted * rate
        rej_value = total_rej * rate

        rej_percent = (total_rej / total_qty * 100) if total_qty else 0

        rubber_qty = 0
        rubber_value = 0

        for c in consumptions:
            rubber_qty += c.quantity_consumed
            rubber_value += float(c.value_consumed)

        cons_percent = (rubber_value / value * 100) if value else 0

        ws.append([
            pe.shift,
            pe.machine.machine_code,
            pe.operator_name or "",
            pe.product.name,
            pe.mould.running_cavity,
            pe.mould.total_cavity,
            pe.planned_quantity,
            pe.produced_quantity,
            "",                      # Shift Qty (optional)
            total_qty,
            rej_p,
            rej_qa,
            rej_fd,
            accepted,
            rate,
            round(value, 2),
            round(rej_value, 2),
            f"{round(rej_percent,2)}%",
            f"{round(rej_percent,2)}%",
            "",                      # Ld Wt (future sensor input)
            round(rubber_qty, 3),
            rate,
            round(rubber_value, 2),
            0,
            0,
            round(rubber_value, 2),
            f"{round(cons_percent,2)}%"
        ])

        grand_value += value
        grand_rej_value += rej_value
        grand_total_cons += rubber_value

    # 🔹 GRAND TOTAL ROW
    ws.append([
        "","","","","","","","","","",
        "","","","",
        "",
        round(grand_value,2),
        round(grand_rej_value,2),
        "","",
        "",
        "",
        "",
        "",
        "",
        "",
        round(grand_total_cons,2),
        f"{round((grand_total_cons/grand_value)*100,2) if grand_value else 0}%"
    ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = (
        f"attachment; filename=Daily_Production_Report_{report_date}.xlsx"
    )

    wb.save(response)
    return response
