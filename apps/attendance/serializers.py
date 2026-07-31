from rest_framework import serializers
from .models import WorkSchedule, Attendance


class WorkScheduleSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)

    class Meta:
        model = WorkSchedule
        fields = "__all__"


class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)
    hours_worked = serializers.FloatField(read_only=True)
    overtime_hours = serializers.FloatField(read_only=True)

    class Meta:
        model = Attendance
        fields = "__all__"
