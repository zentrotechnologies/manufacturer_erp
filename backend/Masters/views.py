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

# Create your views here.



class vendor_list_pagination_api(GenericAPIView):
    pagination_class=CustomPagination

    def post(self,request):
        search=request.data.get('searchtext')
        vendors_obj = Vendor.objects.filter(isActive=True).order_by('name')
        if search is not None and search !='':
            vendors_obj=vendors_obj.filter(Q(name__icontains=search)|Q(contact_number__icontains=search)|Q(address__icontains=search))
            
            
        page4 = self.paginate_queryset(vendors_obj)
        serializer = VendorSerializer(page4,many=True)
        return self.get_paginated_response(serializer.data)            
                    
class add_new_vendor(GenericAPIView):
    

    def post(self,request):
        data=request.data.copy()
        vendors_obj = Vendor.objects.filter(isActive=True,name=data['name']).first()
        if vendors_obj is not None:
            return Response({"data" : [],"response":{"n":0,"msg":"vendor with this name already exists","status":"error"}}) 
        data['isActive']=True
        serializer=VendorSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            
            return Response({
                        "data" : serializer.data,
                        "response":{
                            "n":1,
                            "msg":"New Vendor added",
                            "status":"success"
                        }
                    })

        else:
            
            first_key, first_value = next(iter(serializer.errors.items()))
            return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  

class vendor_list(GenericAPIView):
    serializer_class = VendorSerializer

    def post(self, request):
        search = request.data.get('searchtext')
        vendors = Vendor.objects.filter(isActive=True).order_by('name')

        if search:
            vendors = vendors.filter(
                Q(name__icontains=search) |
                Q(contact_number__icontains=search) |
                Q(address__icontains=search)
            )

        serializer = self.get_serializer(vendors, many=True)
        return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "Vendor list fetched successfully",
                "status": "success"
            }
        })
class get_vendor_by_id(GenericAPIView):
    serializer_class = VendorSerializer

    def post(self, request):
        vendor_id = request.data.get('id')

        if not vendor_id:
            return Response({
                "data": [],
                "response": {"n": 0, "msg": "Vendor ID is required", "status": "error"}
            })

        vendor = Vendor.objects.filter(id=vendor_id, isActive=True).first()

        if not vendor:
            return Response({
                "data": [],
                "response": {"n": 0, "msg": "Vendor not found", "status": "error"}
            })

        serializer = self.get_serializer(vendor)
        return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "Vendor fetched successfully",
                "status": "success"
            }
        })

class update_vendor(GenericAPIView):
    serializer_class = VendorSerializer

    def post(self, request):
        vendor_id = request.data.get('id')

        if not vendor_id:
            return Response({
                "data": [],
                "response": {"n": 0, "msg": "Vendor ID is required", "status": "error"}
            })

        vendor = Vendor.objects.filter(id=vendor_id, isActive=True).first()

        if not vendor:
            return Response({
                "data": [],
                "response": {"n": 0, "msg": "Vendor not found", "status": "error"}
            })

        serializer = self.get_serializer(vendor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "data": serializer.data,
                "response": {
                    "n": 1,
                    "msg": "Vendor updated successfully",
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
class delete_vendor(GenericAPIView):

    def post(self, request):
        vendor_id = request.data.get('id')

        if not vendor_id:
            return Response({
                "data": [],
                "response": {"n": 0, "msg": "Vendor ID is required", "status": "error"}
            })

        vendor = Vendor.objects.filter(id=vendor_id, isActive=True).first()

        if not vendor:
            return Response({
                "data": [],
                "response": {"n": 0, "msg": "Vendor not found", "status": "error"}
            })

        vendor.isActive = False
        vendor.save()

        return Response({
            "data": [],
            "response": {
                "n": 1,
                "msg": "Vendor deleted successfully",
                "status": "success"
            }
        })



class raw_material_list_pagination_api(GenericAPIView):
    pagination_class = CustomPagination

    def post(self, request):
        search = request.data.get('searchtext')
        qs = RawMaterial.objects.filter(isActive=True).order_by('name')

        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(unit__icontains=search) |
                Q(hsn_code__icontains=search) |
                Q(vendor__name__icontains=search)
            )

        page = self.paginate_queryset(qs)
        serializer = CustomRawMaterialSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


 
class add_new_raw_material(GenericAPIView):

    def post(self, request):
        data = request.data.copy()
        name = data.get('name')

        if not name:
            return Response({
                "data": [],
                "response": {"n": 0, "msg": "Raw material name is required", "status": "error"}
            })

        exists = RawMaterial.objects.filter(
            isActive=True,
            name=name,
            vendor_id=data.get('vendor')
        ).exists()

        if exists:
            return Response({
                "data": [],
                "response": {
                    "n": 0,
                    "msg": "Raw material already exists for this vendor",
                    "status": "error"
                }
            })

        data['isActive'] = True
        serializer = RawMaterialSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "data": serializer.data,
                "response": {"n": 1, "msg": "New Raw Material added", "status": "success"}
            })

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({
            "data": serializer.errors,
            "response": {"n": 0, "msg": f"{first_key} : {first_value[0]}", "status": "error"}
        })

class get_raw_material_by_id(GenericAPIView):
    serializer_class = RawMaterialSerializer

    def post(self, request):
        material_id = request.data.get('id')

        if not material_id:
            return Response({
                "data": [],
                "response": {"n": 0, "msg": "Raw Material ID is required", "status": "error"}
            })

        obj = RawMaterial.objects.filter(id=material_id, isActive=True).first()
        if not obj:
            return Response({
                "data": [],
                "response": {"n": 0, "msg": "Raw Material not found", "status": "error"}
            })

        serializer = self.get_serializer(obj)
        return Response({
            "data": serializer.data,
            "response": {"n": 1, "msg": "Raw Material fetched successfully", "status": "success"}
        })
class update_raw_material(GenericAPIView):
    serializer_class = RawMaterialSerializer

    def post(self, request):
        material_id = request.data.get('id')

        obj = RawMaterial.objects.filter(id=material_id, isActive=True).first()
        if not obj:
            return Response({
                "data": [],
                "response": {"n": 0, "msg": "Raw Material not found", "status": "error"}
            })

        serializer = self.get_serializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "data": serializer.data,
                "response": {"n": 1, "msg": "Raw Material updated successfully", "status": "success"}
            })

        first_key, first_value = next(iter(serializer.errors.items()))
        return Response({
            "data": serializer.errors,
            "response": {"n": 0, "msg": f"{first_key} : {first_value[0]}", "status": "error"}
        })
class delete_raw_material(GenericAPIView):

    def post(self, request):
        material_id = request.data.get('id')

        obj = RawMaterial.objects.filter(id=material_id, isActive=True).first()
        if not obj:
            return Response({
                "data": [],
                "response": {"n": 0, "msg": "Raw Material not found", "status": "error"}
            })

        obj.isActive = False
        obj.save()

        return Response({
            "data": [],
            "response": {"n": 1, "msg": "Raw Material deleted successfully", "status": "success"}
        })
class raw_material_list(GenericAPIView):
    serializer_class = RawMaterialSerializer

    def post(self, request):
        search = request.data.get('searchtext')
        materials = RawMaterial.objects.filter(isActive=True).order_by('name')

        if search:
            materials = materials.filter(
                Q(name__icontains=search) |
                Q(unit__icontains=search) |
                Q(hsn_code__icontains=search) |
                Q(vendor__name__icontains=search)
            )

        serializer = self.get_serializer(materials, many=True)
        return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "Raw material list fetched successfully",
                "status": "success"
            }
        })


class machine_list_pagination_api(GenericAPIView):
    pagination_class = CustomPagination
    serializer_class = MachineSerializer

    def post(self, request):
        search = request.data.get('searchtext')
        machines = Machine.objects.filter(isActive=True).order_by('machine_code')

        if search:
            machines = machines.filter(
                Q(machine_code__icontains=search) |
                Q(name__icontains=search)
            )

        page = self.paginate_queryset(machines)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

class add_new_machine(GenericAPIView):
    serializer_class = MachineSerializer

    def post(self, request):
        data = request.data.copy()
        data['isActive']=True
        if Machine.objects.filter(
            isActive=True,
            machine_code=data.get('machine_code')
        ).exists():
            return Response({
                "data": [],
                "response": {
                    "n": 0,
                    "msg": "Machine with this code already exists",
                    "status": "error"
                }
            })

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "data": serializer.data,
                "response": {
                    "n": 1,
                    "msg": "New Machine added",
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

class machine_list(GenericAPIView):
    serializer_class = MachineSerializer

    def post(self, request):
        search = request.data.get('searchtext')
        machines = Machine.objects.filter(isActive=True).order_by('machine_code')

        if search:
            machines = machines.filter(
                Q(machine_code__icontains=search) |
                Q(name__icontains=search)
            )

        serializer = self.get_serializer(machines, many=True)
        return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "Machine list fetched successfully",
                "status": "success"
            }
        })

class get_machine_by_id(GenericAPIView):
    serializer_class = MachineSerializer

    def post(self, request):
        machine_id = request.data.get('id')

        if not machine_id:
            return Response({
                "data": [],
                "response": {"n": 0, "msg": "Machine ID is required", "status": "error"}
            })

        machine = Machine.objects.filter(id=machine_id, isActive=True).first()

        if not machine:
            return Response({
                "data": [],
                "response": {"n": 0, "msg": "Machine not found", "status": "error"}
            })

        serializer = self.get_serializer(machine)
        return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "Machine fetched successfully",
                "status": "success"
            }
        })

class update_machine(GenericAPIView):
    serializer_class = MachineSerializer

    def post(self, request):
        machine_id = request.data.get('id')

        if not machine_id:
            return Response({
                "data": [],
                "response": {"n": 0, "msg": "Machine ID is required", "status": "error"}
            })

        machine = Machine.objects.filter(id=machine_id, isActive=True).first()

        if not machine:
            return Response({
                "data": [],
                "response": {"n": 0, "msg": "Machine not found", "status": "error"}
            })

        serializer = self.get_serializer(machine, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "data": serializer.data,
                "response": {
                    "n": 1,
                    "msg": "Machine updated successfully",
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
class delete_machine(GenericAPIView):

    def post(self, request):
        machine_id = request.data.get('id')

        if not machine_id:
            return Response({
                "data": [],
                "response": {"n": 0, "msg": "Machine ID is required", "status": "error"}
            })

        machine = Machine.objects.filter(id=machine_id, isActive=True).first()

        if not machine:
            return Response({
                "data": [],
                "response": {"n": 0, "msg": "Machine not found", "status": "error"}
            })

        machine.isActive = False
        machine.save()

        return Response({
            "data": [],
            "response": {
                "n": 1,
                "msg": "Machine deleted successfully",
                "status": "success"
            }
        })

class mould_list_pagination_api(GenericAPIView):
    pagination_class = CustomPagination
    serializer_class = CustomMouldSerializer

    def post(self, request):
        search = request.data.get('searchtext')
        moulds = Mould.objects.filter(isActive=True).order_by('mould_code')

        if search:
            moulds = moulds.filter(
                Q(mould_code__icontains=search) |
                Q(machine__machine_code__icontains=search)
            )

        page = self.paginate_queryset(moulds)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
class add_new_mould(GenericAPIView):
    serializer_class = MouldSerializer

    def post(self, request):
        data = request.data.copy()
        data['isActive']=True
        if Mould.objects.filter(
            isActive=True,
            mould_code=data.get('mould_code')
        ).exists():
            return Response({
                "data": [],
                "response": {
                    "n": 0,
                    "msg": "Mould with this code already exists",
                    "status": "error"
                }
            })

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "data": serializer.data,
                "response": {
                    "n": 1,
                    "msg": "New Mould added",
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
class mould_list(GenericAPIView):
    serializer_class = MouldSerializer

    def post(self, request):
        search = request.data.get('searchtext')
        moulds = Mould.objects.filter(isActive=True).order_by('mould_code')

        if search:
            moulds = moulds.filter(
                Q(mould_code__icontains=search) |
                Q(machine__machine_code__icontains=search)
            )

        serializer = self.get_serializer(moulds, many=True)
        return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "Mould list fetched successfully",
                "status": "success"
            }
        })
class get_mould_by_id(GenericAPIView):
    serializer_class = MouldSerializer

    def post(self, request):
        mould_id = request.data.get('id')

        if not mould_id:
            return Response({
                "data": [],
                "response": {"n": 0, "msg": "Mould ID is required", "status": "error"}
            })

        mould = Mould.objects.filter(id=mould_id, isActive=True).first()

        if not mould:
            return Response({
                "data": [],
                "response": {"n": 0, "msg": "Mould not found", "status": "error"}
            })

        serializer = self.get_serializer(mould)
        return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "Mould fetched successfully",
                "status": "success"
            }
        })
class update_mould(GenericAPIView):
    serializer_class = MouldSerializer

    def post(self, request):
        mould_id = request.data.get('id')

        if not mould_id:
            return Response({
                "data": [],
                "response": {"n": 0, "msg": "Mould ID is required", "status": "error"}
            })

        mould = Mould.objects.filter(id=mould_id, isActive=True).first()

        if not mould:
            return Response({
                "data": [],
                "response": {"n": 0, "msg": "Mould not found", "status": "error"}
            })

        serializer = self.get_serializer(mould, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "data": serializer.data,
                "response": {
                    "n": 1,
                    "msg": "Mould updated successfully",
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
class delete_mould(GenericAPIView):

    def post(self, request):
        mould_id = request.data.get('id')

        if not mould_id:
            return Response({
                "data": [],
                "response": {"n": 0, "msg": "Mould ID is required", "status": "error"}
            })

        mould = Mould.objects.filter(id=mould_id, isActive=True).first()

        if not mould:
            return Response({
                "data": [],
                "response": {"n": 0, "msg": "Mould not found", "status": "error"}
            })

        mould.isActive = False
        mould.save()

        return Response({
            "data": [],
            "response": {
                "n": 1,
                "msg": "Mould deleted successfully",
                "status": "success"
            }
        })

class product_list_pagination_api(GenericAPIView):
    pagination_class = CustomPagination

    def post(self, request):
        search = request.data.get('searchtext')
        qs = Product.objects.filter(isActive=True).order_by('name')

        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(part_code__icontains=search)
            )

        page = self.paginate_queryset(qs)
        serializer = ProductSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)
    
    
class add_new_product(GenericAPIView):

    @transaction.atomic
    def post(self, request):
        data = request.data.copy()
        raw_materials = data.pop('raw_materials', [])

        if Product.objects.filter(
            part_code=data.get('part_code'),
            isActive=True
        ).exists():
            return Response({
                "data": [],
                "response": {
                    "n": 0,
                    "msg": "Product with this part code already exists",
                    "status": "error"
                }
            })

        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            product = serializer.save(isActive=True)

            for item in raw_materials:
                ProductConfiguration.objects.create(
                    product=product,
                    raw_material_id=item['raw_material'],
                    quantity=item['quantity']
                )

            return Response({
                "data": serializer.data,
                "response": {
                    "n": 1,
                    "msg": "Product and configuration added successfully",
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
class product_list(GenericAPIView):
    serializer_class = ProductSerializer

    def post(self, request):
        products = Product.objects.filter(isActive=True)
        serializer = self.get_serializer(products, many=True)
        return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "Product list fetched successfully",
                "status": "success"
            }
        })
class get_product_by_id(GenericAPIView):

    def post(self, request):
        product_id = request.data.get('id')

        product = Product.objects.filter(
            id=product_id,
            isActive=True
        ).first()

        if not product:
            return Response({
                "data": [],
                "response": {
                    "n": 0,
                    "msg": "Product not found",
                    "status": "error"
                }
            })

        bom = ProductConfiguration.objects.filter(product=product)
        bom_data = [
            {
                "raw_material": b.raw_material.id,
                "raw_material_name": b.raw_material.name,
                "quantity": b.quantity,
                "unit": b.raw_material.unit
            }
            for b in bom
        ]

        return Response({
            "data": {
                "product": ProductSerializer(product).data,
                "raw_materials": bom_data
            },
            "response": {
                "n": 1,
                "msg": "Product fetched successfully",
                "status": "success"
            }
        })
class update_product(GenericAPIView):

    @transaction.atomic
    def post(self, request):
        product_id = request.data.get('id')
        raw_materials = request.data.get('raw_materials', '[]')

        if isinstance(raw_materials, str):
            raw_materials = json.loads(raw_materials)

        product = Product.objects.filter(id=product_id, isActive=True).first()
        if not product:
            return Response({
                "data": [],
                "response": {"n": 0, "msg": "Product not found", "status": "error"}
            })

        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # ✅ MERGE DUPLICATES
            merged = defaultdict(float)
            for item in raw_materials:
                rm = item.get('raw_material')
                qty = item.get('quantity', 0)
                if rm and qty:
                    merged[int(rm)] += float(qty)

            # Reset BOM
            ProductConfiguration.objects.filter(product=product).delete()

            # Insert merged BOM
            for rm_id, qty in merged.items():
                ProductConfiguration.objects.create(
                    product=product,
                    raw_material_id=rm_id,
                    quantity=qty
                )

            return Response({
                "data": serializer.data,
                "response": {
                    "n": 1,
                    "msg": "Product and configuration updated successfully",
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
class delete_product(GenericAPIView):

    def post(self, request):
        product_id = request.data.get('id')

        product = Product.objects.filter(
            id=product_id,
            isActive=True
        ).first()

        if not product:
            return Response({
                "data": [],
                "response": {
                    "n": 0,
                    "msg": "Product not found",
                    "status": "error"
                }
            })

        product.isActive = False
        product.save()

        return Response({
            "data": [],
            "response": {
                "n": 1,
                "msg": "Product deleted successfully",
                "status": "success"
            }
        })




