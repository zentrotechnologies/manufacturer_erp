from rest_framework import serializers
from .models import *

class BatchSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = BatchMaster
        fields = [
            'id',
            'batch_name',
            'product',
            'product_name',
            'batch_weight_kg',
            'standard_output_qty'
        ]
        
        
class BatchRawMaterialSerializer(serializers.ModelSerializer):


    class Meta:
        model = BatchRawMaterial
        fields = '__all__'