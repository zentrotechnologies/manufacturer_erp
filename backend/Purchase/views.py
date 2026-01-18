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



class create_purchase_invoice(GenericAPIView):

    @transaction.atomic
    def post(self, request):
        data = request.data.copy()
        items = data.get('items', '[]')

        # Parse items safely
        if isinstance(items, str):
            try:
                items = json.loads(items)
            except json.JSONDecodeError:
                items = []

        if not items:
            return Response({
                "data": [],
                "response": {
                    "n": 0,
                    "msg": "At least one purchase item is required",
                    "status": "error"
                }
            })

        # Check duplicate invoice number
        if PurchaseInvoice.objects.filter(
            invoice_number=data.get('invoice_number')
        ).exists():
            return Response({
                "data": [],
                "response": {
                    "n": 0,
                    "msg": "Invoice number already exists",
                    "status": "error"
                }
            })

        base_total = 0
        gst_total = 0
        total_qty = 0

        # ---- CALCULATE TOTALS ----
        for item in items:
            qty = float(item.get('quantity', 0))
            rate = float(item.get('rate_per_unit', 0))
            gst = float(item.get('gst_percentage', 0))

            if qty <= 0 or rate <= 0:
                return Response({
                    "data": [],
                    "response": {
                        "n": 0,
                        "msg": "Quantity and rate must be greater than zero",
                        "status": "error"
                    }
                })

            base = qty * rate
            gst_amt = base * gst / 100

            base_total += base
            gst_total += gst_amt
            total_qty += qty

        same_state=data.get('same_state', True)
        if same_state in ['True','true','TRUE',True]:
            same_state=True
        else:
            same_state=False
        # ---- CREATE PURCHASE INVOICE ----
        invoice = PurchaseInvoice.objects.create(
            invoice_number=data.get('invoice_number'),
            vendor_id=data.get('vendor'),
            invoice_date=data.get('invoice_date'),
            base_amount=base_total,
            gst_amount=gst_total,
            total_amount=base_total + gst_total,
            same_state=same_state,
            payment_status=data.get('payment_status', 'Pending'),
            total_quantity=total_qty,
            total_weight=total_qty  # adjust if weight differs
        )

        # ---- CREATE ITEMS + STOCK LEDGER ----
        for item in items:
            qty = float(item['quantity'])
            rate = float(item['rate_per_unit'])
            gst = float(item['gst_percentage'])

            base = qty * rate
            gst_amt = base * gst / 100

            raw_material = RawMaterial.objects.get(id=item['raw_material'])

            PurchaseItem.objects.create(
                purchase_invoice=invoice,
                raw_material=raw_material,
                hsn_code=raw_material.hsn_code,
                quantity=qty,
                gst_percentage=gst,
                rate_per_unit=rate,
                base_amount=base,
                gst_amount=gst_amt,
                total_amount=base + gst_amt
            )

            # ---- STOCK LEDGER ENTRY (IN) ----
            last_entry = RawMaterialStockLedger.objects.filter(
                raw_material=raw_material
            ).order_by('-id').first()

            previous_balance = (
                last_entry.balance_quantity if last_entry else 0
            )

            new_balance = previous_balance + qty

            RawMaterialStockLedger.objects.create(
                raw_material=raw_material,
                purchase_invoice=invoice,
                transaction_type='IN',
                quantity=qty,
                rate_per_unit=rate,
                balance_quantity=new_balance,
                remarks=f"Purchase Invoice {invoice.invoice_number}"
            )

        return Response({
            "data": {
                "invoice_id": invoice.id,
                "invoice_number": invoice.invoice_number
            },
            "response": {
                "n": 1,
                "msg": "Purchase invoice created successfully",
                "status": "success"
            }
        })


class purchase_invoice_list_pagination_api(GenericAPIView):
    pagination_class = CustomPagination

    def post(self, request):
        search = request.data.get('searchtext')

        qs = PurchaseInvoice.objects.filter(isActive=True).order_by('-invoice_date')

        if search:
            qs = qs.filter(
                Q(invoice_number__icontains=search) |
                Q(vendor__name__icontains=search)
            )

        page = self.paginate_queryset(qs)
        serializer = CustomPurchaseInvoiceSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)
class purchase_invoice_list(GenericAPIView):
    serializer_class = PurchaseInvoiceSerializer

    def post(self, request):
        invoices = PurchaseInvoice.objects.filter(isActive=True).order_by('-id')
        serializer = self.get_serializer(invoices, many=True)
        return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "Purchase invoices fetched",
                "status": "success"
            }
        })
class get_purchase_invoice_by_id(GenericAPIView):

    def post(self, request):
        invoice_id = request.data.get('id')

        invoice = PurchaseInvoice.objects.filter(
            id=invoice_id,
            isActive=True
        ).first()

        if not invoice:
            return Response({
                "data": [],
                "response": {
                    "n": 0,
                    "msg": "Invoice not found",
                    "status": "error"
                }
            })

        items = PurchaseItem.objects.filter(
            purchase_invoice=invoice,
            isActive=True
        )

        return Response({
            "data": {
                "invoice": CustomPurchaseInvoiceSerializer(invoice).data,
                "items": CustomPurchaseItemSerializer(items, many=True).data
            },
            "response": {
                "n": 1,
                "msg": "Purchase invoice fetched",
                "status": "success"
            }
        })














