from rest_framework import serializers
from .models import LeaveType, LeaveRequest


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = "__all__"


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)
    leave_type_name = serializers.CharField(source="leave_type.name", read_only=True)
    days_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = LeaveRequest
        fields = "__all__"
        read_only_fields = ("status", "validated_by", "validated_at")
