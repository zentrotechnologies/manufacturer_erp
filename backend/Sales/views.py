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
from decimal import Decimal, ROUND_HALF_UP

# Create your views here.
class create_sales_invoice(GenericAPIView):

    @transaction.atomic
    def post(self, request):

        data = request.data
        items = json.loads(data.get('items', '[]'))
        if data['customer'] is None or data['customer'] =='':
            return Response({
                    "response":{
                        "n":0,
                        "msg":"Please select customer",
                        "status":"error"
                    }
                })
        customer = Customer.objects.get(id=data['customer'])

        base_total = Decimal('0')
        gst_total = Decimal('0')
        already_exist_obj=SalesInvoice.objects.filter(invoice_number=data['invoice_number']).first()
        if already_exist_obj is not None:
            return Response({
                    "response":{
                        "n":0,
                        "msg":"Invoice No already exists",
                        "status":"error"
                    }
                })
            
        for item in items:
            product = Product.objects.get(id=item['product'])
            qty = float(item['quantity'])
            hsn = item.get('hsn_code') or product.hsn_code

            # 🔴 CHECK FG STOCK
            fg = ProductionInventory.objects.filter(product=product).first()
            available = fg.quantity if fg else 0

            if available < qty:
                return Response({
                    "response":{
                        "n":0,
                        "msg":f"Insufficient stock for {product.name}",
                        "status":"error"
                    }
                })
                
                
        invoice = SalesInvoice.objects.create(
            invoice_number=data['invoice_number'],
            invoice_date=data['invoice_date'],
            customer=customer,
            buyer_order_no=data.get('buyer_order_no'),
            buyer_order_date=data.get('buyer_order_date'),
            same_state=data.get('same_state') == 'true',
            base_amount=0,
            gst_amount=0,
            total_amount=0
        )

        for item in items:
            product = Product.objects.get(id=item['product'])
            qty = float(item['quantity'])
            hsn = item.get('hsn_code') or product.hsn_code

            # 🔴 CHECK FG STOCK
            fg = ProductionInventory.objects.filter(product=product).first()
            available = fg.quantity if fg else 0

            if available < qty:
                return Response({
                    "response":{
                        "n":0,
                        "msg":f"Insufficient stock for {product.name}",
                        "status":"error"
                    }
                })

            rate = Decimal(item['rate'])
            gst_per = Decimal(item['gst_percentage'])

            base = Decimal(qty) * rate
            gst_amt = base * gst_per / 100
            total = base + gst_amt

            SalesInvoiceItem.objects.create(
                sales_invoice=invoice,
                product=product,
                hsn_code=hsn, 
                quantity=qty,
                rate_per_unit=rate,
                base_amount=base,
                gst_percentage=gst_per,
                gst_amount=gst_amt,
                total_amount=total
            )

            # FG STOCK OUT
            fg.quantity -= qty
            fg.save()

            FinishedGoodsStockLedger.objects.create(
                product=product,
                sales_invoice=invoice,
                transaction_type='OUT',
                quantity=qty,
                balance_quantity=fg.quantity,
                remarks=f"Sales Invoice {invoice.invoice_number}"
            )

            base_total += base
            gst_total += gst_amt

        invoice.base_amount = base_total
        invoice.gst_amount = gst_total
        invoice.total_amount = base_total + gst_total
        invoice.save()

        return Response({
            "data":{"invoice_id":invoice.id},
            "response":{
                "n":1,
                "msg":"Sales invoice created successfully",
                "status":"success"
            }
        })




# Sales/views.py


class sales_invoice_list_pagination_api(GenericAPIView):
    serializer_class = SalesInvoiceListSerializer
    pagination_class = CustomPagination

    def post(self, request):
        search = request.data.get('searchtext')

        qs = SalesInvoice.objects.filter(
            isActive=True
        ).order_by('-invoice_date', '-id')

        if search:
            qs = qs.filter(
                Q(invoice_number__icontains=search) |
                Q(customer__name__icontains=search)
            )

        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True)

        return self.get_paginated_response(serializer.data)
    
    
class get_sales_invoice_by_id(GenericAPIView):

    def post(self, request):
        invoice_id = request.data.get('id')

        if not invoice_id:
            return Response({
                "data": [],
                "response": {
                    "n": 0,
                    "msg": "Invoice ID is required",
                    "status": "error"
                }
            })

        invoice = SalesInvoice.objects.filter(
            id=invoice_id,
            isActive=True
        ).select_related('customer').first()

        if not invoice:
            return Response({
                "data": [],
                "response": {
                    "n": 0,
                    "msg": "Sales invoice not found",
                    "status": "error"
                }
            })

        items = SalesInvoiceItem.objects.filter(
            sales_invoice=invoice,
            isActive=True
        ).select_related('product')

        # --- Invoice Header ---
        invoice_data = {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "invoice_date": invoice.invoice_date,
            "same_state": invoice.same_state,
            "base_amount": float(invoice.base_amount),
            "gst_amount": float(invoice.gst_amount),
            "total_amount": float(invoice.total_amount),
            "payment_status": invoice.payment_status,

            "customer": {
                "id": invoice.customer.id if invoice.customer else None,
                "name": invoice.customer.name if invoice.customer else "",
                "gstin": invoice.customer.gstin if invoice.customer else "",
                "address": invoice.customer.address if invoice.customer else "",
                "contact_number": invoice.customer.mobile if invoice.customer else ""
            }
        }

        # --- Items ---
        items_data = []
        for i in items:
            items_data.append({
                "product_id": i.product.id,
                "product_name": i.product.name,
                "hsn_code": i.hsn_code,
                "quantity": float(i.quantity),
                "rate": float(i.rate_per_unit),
                "gst_percentage": float(i.gst_percentage),
                "base_amount": float(i.base_amount),
                "gst_amount": float(i.gst_amount),
                "total_amount": float(i.total_amount)
            })

        return Response({
            "data": {
                "invoice": invoice_data,
                "items": items_data
            },
            "response": {
                "n": 1,
                "msg": "Sales invoice fetched successfully",
                "status": "success"
            }
        })
        
        
        
        