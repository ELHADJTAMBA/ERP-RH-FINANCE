import datetime
from decimal import Decimal

from django.db.models import Sum, Count, Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.employees.models import Employee, SafetyIncident, EPIDistribution
from apps.contracts.models import Contract
from apps.attendance.models import Attendance
from apps.leave_management.models import LeaveRequest
from apps.payroll.models import Payslip, PayrollRun
from apps.accounting.models import Invoice, Budget, JournalEntry, FixedAsset


class HRDashboardView(APIView):
    """
    GET /api/dashboard/hr/
    Indicateurs RH: effectifs, taux d'absentéisme, masse salariale (Module 3.A).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = datetime.date.today()
        total_employees = Employee.objects.filter(status=Employee.Status.ACTIVE).count()

        by_category = list(
            Employee.objects.filter(status=Employee.Status.ACTIVE)
            .values("category").annotate(count=Count("id")).order_by("category")
        )
        by_site = list(
            Employee.objects.filter(status=Employee.Status.ACTIVE)
            .values("site__name").annotate(count=Count("id")).order_by("site__name")
        )

        month_start = today.replace(day=1)
        attendances_this_month = Attendance.objects.filter(date__gte=month_start, date__lte=today)
        total_records = attendances_this_month.count()
        absences = attendances_this_month.filter(status=Attendance.Status.ABSENT).count()
        absenteeism_rate = round((absences / total_records) * 100, 2) if total_records else 0

        last_payroll = PayrollRun.objects.order_by("-period_year", "-period_month").first()
        payroll_mass = last_payroll.total_net if last_payroll else Decimal("0")

        expiring_contracts = Contract.objects.filter(
            status=Contract.ContractStatus.ACTIVE,
            end_date__isnull=False,
            end_date__gte=today,
            end_date__lte=today + datetime.timedelta(days=30),
        ).count()

        pending_leaves = LeaveRequest.objects.filter(status=LeaveRequest.RequestStatus.PENDING).count()

        return Response({
            "total_active_employees": total_employees,
            "by_category": by_category,
            "by_site": by_site,
            "absenteeism_rate_percent": absenteeism_rate,
            "payroll_mass_last_run": payroll_mass,
            "contracts_expiring_30_days": expiring_contracts,
            "pending_leave_requests": pending_leaves,
        })


class FinanceDashboardView(APIView):
    """
    GET /api/dashboard/finance/
    Vue d'ensemble financière: revenus, dépenses, marge (Module 3.A).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = datetime.date.today()
        year = today.year

        revenue = Invoice.objects.filter(issue_date__year=year).aggregate(total=Sum("amount"))["total"] or Decimal("0")
        collected = Invoice.objects.filter(issue_date__year=year).aggregate(total=Sum("amount_paid"))["total"] or Decimal("0")
        outstanding = revenue - collected

        expenses = JournalEntry.objects.filter(
            date__year=year, account__account_type="EXPENSE"
        ).aggregate(total=Sum("debit"))["total"] or Decimal("0")

        margin = revenue - expenses

        overdue_invoices = Invoice.objects.filter(
            due_date__lt=today
        ).exclude(status=Invoice.InvoiceStatus.PAID).count()

        over_budget_lines = sum(1 for b in Budget.objects.filter(year=year) if b.is_over_budget)

        return Response({
            "year": year,
            "total_revenue": revenue,
            "total_collected": collected,
            "outstanding_receivables": outstanding,
            "total_expenses": expenses,
            "margin": margin,
            "overdue_invoices_count": overdue_invoices,
            "budget_lines_over_forecast": over_budget_lines,
        })


class OperationsDashboardView(APIView):
    """
    GET /api/dashboard/operations/
    Indicateurs opérationnels: tonnes transportées, immobilisations (Module 3.A).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = datetime.date.today()
        year = today.year

        tonnage = Invoice.objects.filter(issue_date__year=year).aggregate(total=Sum("tonnage"))["total"] or Decimal("0")

        fleet_count = FixedAsset.objects.filter(category=FixedAsset.AssetCategory.TRUCK, is_active=True).count()
        fleet_value = FixedAsset.objects.filter(is_active=True).aggregate(
            total=Sum("acquisition_value")
        )["total"] or Decimal("0")
        fleet_nbv = sum((a.net_book_value for a in FixedAsset.objects.filter(is_active=True)), Decimal("0"))

        return Response({
            "year": year,
            "total_tonnage_transported": tonnage,
            "active_fleet_count": fleet_count,
            "fleet_acquisition_value": fleet_value,
            "fleet_net_book_value": fleet_nbv,
        })


class HSSEDashboardView(APIView):
    """
    GET /api/dashboard/hsse/
    KPIs HSSE: accidents, incidents, conformité EPI (Module 3.A).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = datetime.date.today()
        year = today.year

        incidents_qs = SafetyIncident.objects.filter(incident_date__year=year)
        by_severity = list(incidents_qs.values("severity").annotate(count=Count("id")))
        total_incidents = incidents_qs.count()
        open_incidents = incidents_qs.exclude(status=SafetyIncident.IncidentStatus.CLOSED).count()

        epi_cost_ytd = EPIDistribution.objects.filter(
            distribution_date__year=year
        ).aggregate(total=Sum("unit_cost"))["total"] or Decimal("0")

        epi_renewals_due = EPIDistribution.objects.filter(
            renewal_due_date__gte=today,
            renewal_due_date__lte=today + datetime.timedelta(days=30),
        ).count()

        return Response({
            "year": year,
            "total_incidents": total_incidents,
            "open_incidents": open_incidents,
            "incidents_by_severity": by_severity,
            "epi_cost_year_to_date": epi_cost_ytd,
            "epi_renewals_due_30_days": epi_renewals_due,
        })
