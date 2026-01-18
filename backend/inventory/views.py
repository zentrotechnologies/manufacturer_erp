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
from django.db import transaction
from collections import defaultdict

class raw_material_inventory_list_pagination_api(GenericAPIView):
    pagination_class = CustomPagination

    def post(self, request):
        search = request.data.get('searchtext')

        raw_materials = RawMaterial.objects.filter(isActive=True)

        if search:
            raw_materials = raw_materials.filter(
                Q(name__icontains=search)
            )

        data = []

        for rm in raw_materials:
            last_entry = RawMaterialStockLedger.objects.filter(
                raw_material=rm
            ).order_by('-id').first()

            data.append({
                "raw_material": rm.name,
                "unit": rm.unit,
                "current_stock": last_entry.balance_quantity if last_entry else 0,
                "last_rate": last_entry.rate_per_unit if last_entry else None,
                "last_transaction": last_entry.remarks if last_entry else None,
            })

        page = self.paginate_queryset(data)
        serializer = RawMaterialInventorySerializer(page, many=True)
        return self.get_paginated_response(serializer.data)





class production_inventory_list_pagination_api(GenericAPIView):
    pagination_class = CustomPagination

    def post(self, request):
        search = request.data.get('searchtext')

        qs = ProductionInventory.objects.select_related(
            'product'
        ).filter(isActive=True).order_by('product__name')

        if search:
            qs = qs.filter(
                Q(product__name__icontains=search) |
                Q(product__part_code__icontains=search)
            )

        page = self.paginate_queryset(qs)

        data = []
        for obj in page:
            data.append({
                "id": obj.id,
                "product": obj.product.name,
                "part_code": obj.product.part_code,
                "quantity": obj.quantity
            })

        return self.get_paginated_response(data)



