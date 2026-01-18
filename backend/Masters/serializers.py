
from .models import *
from rest_framework import serializers

class VendorSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= Vendor
        fields='__all__'
        
class RawMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawMaterial
        fields = "__all__"
class CustomRawMaterialSerializer(serializers.ModelSerializer):
    vendor_name= serializers.SerializerMethodField()
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
    class Meta:
        model = RawMaterial
        fields = "__all__"
class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = "__all__"

class MouldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mould
        fields = "__all__"

class CustomMouldSerializer(serializers.ModelSerializer):
    
    machine_name= serializers.SerializerMethodField()
    def get_machine_name(self, obj):
        obj_id = obj.machine_id
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                obj = Machine.objects.filter(id=obj_id).first()
                if obj is not None:
                   return obj.name
                else:
                    return None
            except Machine.DoesNotExist:
                return None
        return None
    machine_code= serializers.SerializerMethodField()
    def get_machine_code(self, obj):
        obj_id = obj.machine_id
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                obj = Machine.objects.filter(id=obj_id).first()
                if obj is not None:
                   return obj.machine_code
                else:
                    return None
            except Machine.DoesNotExist:
                return None
        return None
    class Meta:
        model = Mould
        fields = "__all__"
class NormalProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        
        
class ProductConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductConfiguration
        fields = ('raw_material', 'quantity')
        
class ProductSerializer(serializers.ModelSerializer):
    raw_materials = ProductConfigurationSerializer(
        many=True,
        write_only=True,
        required=False
    )

    class Meta:
        model = Product
        fields = (
            'id', 'part_code', 'name', 'mould',
            'hsn_code', 'price_per_unit', 'gst_percentage',
            'raw_materials'
        )
