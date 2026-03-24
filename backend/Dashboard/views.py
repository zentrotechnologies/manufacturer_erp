from django.shortcuts import render

from rest_framework.authentication import (BaseAuthentication,
                                           get_authorization_header)
from rest_framework import permissions
from rest_framework.response import Response
import json
from rest_framework.generics import GenericAPIView
from django.contrib.auth import authenticate
from .models import *
from .serializers import *
from User.models import *
from User.serializers import *

from User.jwt import userJWTAuthentication
from django.template.loader import get_template, render_to_string
from django.core.mail import EmailMessage
from manufacturer_erp.settings import EMAIL_HOST_USER
from User.common import CustomPagination
from django.db.models import Q
from django.db.models import F, FloatField
from django.db.models.functions import Cast
from helpers.custom_functions import *
from django.db.models import Count
from django.utils.timezone import now
from django.db.models import Sum
from datetime import date

from Production.models import *
from inventory.models import *
from Purchase.models import *
from Sales.models import *
from Masters.models import *
from collections import defaultdict


class dashboard_analytics_api(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        profit_loss_statement = '0'  # Placeholder for profit/loss statement, can be calculated based on your business logic
        current_month = datetime.now().month
        current_month_year = datetime.now().year
        previous_month = current_month - 1 if current_month > 1 else 12
        previous_month_year = datetime.now().year if current_month > 1 else datetime.now().year - 1





        return Response({

        })  
    
# backend/Dashboard/views.py



class dashboard_summary_api(GenericAPIView):

    def get(self, request):

        today = date.today()
        month_start = today.replace(day=1)

        # ===============================
        # TODAY PRODUCTION (SUMMARY)
        # ===============================
        prod_qs = ProductionEntry.objects.filter(
            production_date=today,
            isActive=True
        )

        today_production = sum(
            (p.produced_quantity - p.rejected_quantity)
            for p in prod_qs
        )

        # ---- Today production detail (machine + product)
        prod_map = defaultdict(float)
        for p in prod_qs:
            key = (p.machine.machine_code, p.product.name)
            prod_map[key] += (p.produced_quantity - p.rejected_quantity)

        today_production_detail = [
            {
                "machine": k[0],
                "product": k[1],
                "qty": v
            } for k, v in prod_map.items()
        ]

        # ===============================
        # LOW STOCK
        # ===============================
        low_stock_items = []
        for rm in RawMaterial.objects.filter(isActive=True):
            last = RawMaterialStockLedger.objects.filter(
                raw_material=rm
            ).order_by('-id').first()

            if last and last.balance_quantity < 10:
                low_stock_items.append({
                    "name": rm.name,
                    "qty": last.balance_quantity,
                    "unit": rm.unit
                })

        # ===============================
        # PENDING PURCHASE
        # ===============================
        pending_qs = PurchaseInvoice.objects.filter(
            payment_status='Pending',
            isActive=True
        )

        pending_purchase = pending_qs.aggregate(
            total=Sum('total_amount')
        )['total'] or 0

        pending_purchase_list = [
            {
                "invoice": p.invoice_number,
                "amount": float(p.total_amount)
            }
            for p in pending_qs.order_by('-id')[:5]
        ]

        # ===============================
        # SALES
        # ===============================
        sales_today_qs = SalesInvoice.objects.filter(
            invoice_date=today,
            isActive=True
        )

        today_sales = sales_today_qs.aggregate(
            total=Sum('total_amount')
        )['total'] or 0

        today_sales_qty = SalesInvoiceItem.objects.filter(
            sales_invoice__invoice_date=today,
            sales_invoice__isActive=True
        ).aggregate(
            qty=Sum('quantity')
        )['qty'] or 0

        monthly_sales = SalesInvoice.objects.filter(
            invoice_date__gte=month_start,
            isActive=True
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or 0

        # ===============================
        # RECENT ACTIVITY
        # ===============================
        recent_activity = []

        for p in ProductionEntry.objects.order_by('-id')[:3]:
            recent_activity.append(
                f"⚙️ Production Entry #{p.id} ({p.product.name})"
            )

        for s in SalesInvoice.objects.order_by('-id')[:2]:
            recent_activity.append(
                f"💰 Sales Invoice #{s.invoice_number}"
            )

        # ===============================
        # RESPONSE
        # ===============================
        return Response({
            "data": {
                # KPIs
                "today_production": today_production,
                "low_stock_count": len(low_stock_items),
                "pending_purchase": pending_purchase,
                "monthly_sales": monthly_sales,

                # NEW (extended)
                "today_production_detail": today_production_detail,
                "low_stock_items": low_stock_items,
                "pending_purchase_list": pending_purchase_list,
                "today_sales": today_sales,
                "today_sales_qty": today_sales_qty,
                "recent_activity": recent_activity
            },
            "response": {
                "n": 1,
                "status": "success"
            }
        })







# adjust imports as per your project

class DashboardSummaryAPI(GenericAPIView):

    def get(self, request):

        today = date.today()

        # =========================
        # TODAY PRODUCTION
        # =========================
        today_qs = ProductionEntry.objects.filter(
            production_date=today,
            isActive=True
        )

        today_production = sum(p.accepted_qty for p in today_qs)

        today_production_detail = [
            {
                "machine": p.machine.machine_code,
                "product": p.product.name,
                "qty": p.accepted_qty
            }
            for p in today_qs
        ]

        # =========================
        # LOW STOCK
        # =========================
        low_stock_items = []

        materials = RawMaterial.objects.all()

        for rm in materials:
            last = RawMaterialStockLedger.objects.filter(
                raw_material=rm
            ).order_by('-id').first()

            balance = last.balance_quantity if last else 0

            if balance < 50:   # 🔥 threshold (you can make dynamic)
                low_stock_items.append({
                    "name": rm.name,
                    "qty": float(balance),
                    "unit": "KG"
                })

        # =========================
        # PENDING PURCHASE (DUMMY for now)
        # =========================
        pending_purchase = 0
        pending_purchase_list = []

        # =========================
        # SALES (DUMMY for now)
        # =========================
        today_sales = 0
        monthly_sales = 0
        today_sales_qty = 0

        # =========================
        # RECENT ACTIVITY
        # =========================
        recent_activity = []

        last_entries = ProductionEntry.objects.filter(
            isActive=True
        ).order_by('-id')[:5]

        for p in last_entries:
            recent_activity.append(
                f"{p.product.name} produced {p.accepted_qty} on {p.production_date}"
            )

        return Response({
            "data": {
                "today_production": today_production,
                "today_production_detail": today_production_detail,

                "low_stock_count": len(low_stock_items),
                "low_stock_items": low_stock_items,

                "pending_purchase": pending_purchase,
                "pending_purchase_list": pending_purchase_list,

                "today_sales": today_sales,
                "monthly_sales": monthly_sales,
                "today_sales_qty": today_sales_qty,

                "recent_activity": recent_activity
            },
            "response": {
                "n": 1,
                "msg": "Dashboard data",
                "status": "success"
            }
        })










