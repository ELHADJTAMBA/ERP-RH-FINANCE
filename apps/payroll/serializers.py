from rest_framework import serializers
from .models import SalaryGrid, PayrollRun, Payslip


class SalaryGridSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryGrid
        fields = "__all__"


class PayslipSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)
    matricule = serializers.CharField(source="employee.matricule", read_only=True)

    class Meta:
        model = Payslip
        fields = "__all__"
        read_only_fields = ("cnss_deduction", "tax_deduction", "gross_salary", "net_salary")


class PayrollRunSerializer(serializers.ModelSerializer):
    total_net = serializers.DecimalField(max_digits=16, decimal_places=2, read_only=True)
    payslip_count = serializers.IntegerField(source="payslips.count", read_only=True)

    class Meta:
        model = PayrollRun
        fields = "__all__"
        read_only_fields = ("generated_by", "validated_at")
