import django.utils.timezone as tz
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response

from core.base import AuditLoggingModelViewSet
from core.permissions import IsComptableOrAbove, IsOwnerOrRHOrAbove
from apps.employees.models import Employee
from .models import SalaryGrid, PayrollRun, Payslip
from .serializers import SalaryGridSerializer, PayrollRunSerializer, PayslipSerializer


class SalaryGridViewSet(AuditLoggingModelViewSet):
    queryset = SalaryGrid.objects.all()
    serializer_class = SalaryGridSerializer
    permission_classes = [IsComptableOrAbove]


class PayrollRunViewSet(AuditLoggingModelViewSet):
    """
    Gestion des cycles de paie mensuels.
    `generate_payslips`: crée automatiquement un bulletin brouillon pour
    chaque employé actif ayant un contrat en cours, à partir de son salaire
    de base contractuel.
    """
    queryset = PayrollRun.objects.all()
    serializer_class = PayrollRunSerializer
    permission_classes = [IsComptableOrAbove]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["period_year", "period_month", "status"]

    def perform_create(self, serializer):
        instance = serializer.save(generated_by=self.request.user)
        self._log("CREATE", instance)

    @action(detail=True, methods=["post"])
    def generate_payslips(self, request, pk=None):
        payroll_run = self.get_object()
        created = 0
        for employee in Employee.objects.filter(status=Employee.Status.ACTIVE):
            active_contract = employee.contracts.filter(status="ACTIVE").order_by("-start_date").first()
            if not active_contract:
                continue
            payslip, was_created = Payslip.objects.get_or_create(
                payroll_run=payroll_run, employee=employee,
                defaults={"base_salary": active_contract.base_salary},
            )
            if was_created:
                payslip.compute()
                created += 1
        return Response({"detail": f"{created} bulletin(s) généré(s)."})

    @action(detail=True, methods=["post"])
    def validate_run(self, request, pk=None):
        payroll_run = self.get_object()
        payroll_run.status = PayrollRun.RunStatus.VALIDATED
        payroll_run.validated_at = tz.now()
        payroll_run.save(update_fields=["status", "validated_at"])
        self._log("UPDATE", payroll_run)
        return Response(self.get_serializer(payroll_run).data)


class PayslipViewSet(AuditLoggingModelViewSet):
    queryset = Payslip.objects.select_related("employee", "payroll_run").all()
    serializer_class = PayslipSerializer
    permission_classes = [IsOwnerOrRHOrAbove]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["employee", "payroll_run"]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role == "EMPLOYE":
            return qs.filter(employee__user=self.request.user)
        return qs

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.compute()
        self._log("CREATE", instance)

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.compute()
        self._log("UPDATE", instance)
