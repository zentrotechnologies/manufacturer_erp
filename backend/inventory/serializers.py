from rest_framework import serializers

class RawMaterialInventorySerializer(serializers.Serializer):
    raw_material = serializers.CharField()
    unit = serializers.CharField()
    current_stock = serializers.FloatField()
    last_rate = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    last_transaction = serializers.CharField(allow_null=True)
