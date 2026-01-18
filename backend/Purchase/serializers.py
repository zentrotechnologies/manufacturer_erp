
from .models import *
from rest_framework import serializers

class PurchaseInvoiceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= PurchaseInvoice
        fields='__all__'

class CustomPurchaseInvoiceSerializer(serializers.ModelSerializer):
    vendor_name = serializers.SerializerMethodField()
    def get_vendor_name(self, obj):
        obj_id = obj.vendor_id
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                obj = Vendor.objects.filter(id=obj_id).first()
                if obj is not None:
                   return obj.name
                else:
                    return None
            except Vendor.DoesNotExist:
                return None
        return None
    
    vendor_details = serializers.SerializerMethodField()

    def get_vendor_details(self, obj):
        vendor = obj.vendor
        if not vendor:
            return None

        return {
            "name": vendor.name,
            "address": vendor.address,
            "gstin": vendor.gstin,
            "contact_number": vendor.contact_number
        }
    class Meta:
        model= PurchaseInvoice
        fields='__all__'
        
        
class PurchaseItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= PurchaseItem
        fields='__all__'
        
class CustomPurchaseItemSerializer(serializers.ModelSerializer):
    raw_material_name = serializers.SerializerMethodField()
    def get_raw_material_name(self, obj):
        obj_id = obj.raw_material_id
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                obj = RawMaterial.objects.filter(id=obj_id).first()
                if obj is not None:
                   return obj.name
                else:
                    return None
            except RawMaterial.DoesNotExist:
                return None
        return None
    class Meta:
        model= PurchaseItem
        fields='__all__'
        
        
        
        
        
        
        
        
        
        