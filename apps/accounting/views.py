import django.utils.timezone as tz
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response

from core.base import AuditLoggingModelViewSet
from core.permissions import IsComptableOrAbove, IsOperationalOrAbove
from .models import (
    Account, JournalEntry, Budget, Supplier, PurchaseRequest, PurchaseOrder,
    BankAccount, TreasuryForecast, FixedAsset, Invoice,
)
from .serializers import (
    AccountSerializer, JournalEntrySerializer, BudgetSerializer, SupplierSerializer,
    PurchaseRequestSerializer, PurchaseOrderSerializer, BankAccountSerializer,
    TreasuryForecastSerializer, FixedAssetSerializer, InvoiceSerializer,
)


# --- A. Comptabilité générale -------------------------------------------------

class AccountViewSet(AuditLoggingModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsComptableOrAbove]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["account_type", "is_active"]


class JournalEntryViewSet(AuditLoggingModelViewSet):
    queryset = JournalEntry.objects.select_related("account").all()
    serializer_class = JournalEntrySerializer
    permission_classes = [IsComptableOrAbove]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["account", "currency", "reconciled", "date"]

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        self._log("CREATE", instance)


# --- B. Budgets ----------------------------------------------------------------

class BudgetViewSet(AuditLoggingModelViewSet):
    queryset = Budget.objects.select_related("department").all()
    serializer_class = BudgetSerializer
    permission_classes = [IsComptableOrAbove]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["department", "month", "year"]

    @action(detail=False, methods=["get"])
    def over_budget(self, request):
        """GET /api/budgets/over_budget/ -> lignes ayant dépassé le prévisionnel."""
        qs = [b for b in self.get_queryset() if b.is_over_budget]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


# --- C. Achats et fournisseurs --------------------------------------------------

class SupplierViewSet(AuditLoggingModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsComptableOrAbove]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["category", "is_active"]


class PurchaseRequestViewSet(AuditLoggingModelViewSet):
    """Demandes d'achat: créées par les Resp. Opérationnels/RH, validées par Comptable/Super Admin."""
    queryset = PurchaseRequest.objects.select_related("department", "requested_by").all()
    serializer_class = PurchaseRequestSerializer
    permission_classes = [IsOperationalOrAbove]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["department", "status"]

    def perform_create(self, serializer):
        instance = serializer.save(requested_by=self.request.user)
        self._log("CREATE", instance)

    @action(detail=True, methods=["post"], permission_classes=[IsComptableOrAbove])
    def approve(self, request, pk=None):
        pr = self.get_object()
        pr.status = PurchaseRequest.RequestStatus.APPROVED
        pr.approved_by = request.user
        pr.approved_at = tz.now()
        pr.save(update_fields=["status", "approved_by", "approved_at"])
        self._log("UPDATE", pr)
        return Response(self.get_serializer(pr).data)

    @action(detail=True, methods=["post"], permission_classes=[IsComptableOrAbove])
    def reject(self, request, pk=None):
        pr = self.get_object()
        pr.status = PurchaseRequest.RequestStatus.REJECTED
        pr.approved_by = request.user
        pr.approved_at = tz.now()
        pr.save(update_fields=["status", "approved_by", "approved_at"])
        self._log("UPDATE", pr)
        return Response(self.get_serializer(pr).data)


class PurchaseOrderViewSet(AuditLoggingModelViewSet):
    queryset = PurchaseOrder.objects.select_related("supplier", "purchase_request").all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsComptableOrAbove]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["supplier", "status"]


# --- D. Trésorerie ---------------------------------------------------------------

class BankAccountViewSet(AuditLoggingModelViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
    permission_classes = [IsComptableOrAbove]


class TreasuryForecastViewSet(AuditLoggingModelViewSet):
    queryset = TreasuryForecast.objects.all()
    serializer_class = TreasuryForecastSerializer
    permission_classes = [IsComptableOrAbove]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["month", "year"]


# --- E. Immobilisations ------------------------------------------------------------

class FixedAssetViewSet(AuditLoggingModelViewSet):
    queryset = FixedAsset.objects.select_related("site").all()
    serializer_class = FixedAssetSerializer
    permission_classes = [IsComptableOrAbove]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["category", "site", "is_active"]

    @action(detail=True, methods=["post"])
    def apply_depreciation(self, request, pk=None):
        """POST /api/fixed-assets/{id}/apply_depreciation/ -> applique l'amortissement du mois."""
        asset = self.get_object()
        increment = asset.apply_monthly_depreciation()
        self._log("UPDATE", asset)
        return Response({"depreciation_applied": increment, "net_book_value": asset.net_book_value})

    @action(detail=False, methods=["post"])
    def apply_depreciation_all(self, request):
        """Applique l'amortissement mensuel à toutes les immobilisations actives (tâche planifiée)."""
        count = 0
        for asset in self.get_queryset().filter(is_active=True):
            asset.apply_monthly_depreciation()
            count += 1
        return Response({"detail": f"Amortissement appliqué à {count} immobilisation(s)."})


# --- F. Facturation -----------------------------------------------------------------

class InvoiceViewSet(AuditLoggingModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsComptableOrAbove]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "client_name"]

    @action(detail=False, methods=["get"])
    def overdue(self, request):
        """GET /api/invoices/overdue/ -> factures impayées et échues (relances)."""
        import datetime
        qs = self.get_queryset().filter(
            due_date__lt=datetime.date.today()
        ).exclude(status=Invoice.InvoiceStatus.PAID)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
