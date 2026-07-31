from rest_framework import serializers
from .models import Contract


class ContractSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)
    is_expiring_soon = serializers.BooleanField(read_only=True)
    days_until_expiry = serializers.IntegerField(read_only=True)

    class Meta:
        model = Contract
        fields = "__all__"
