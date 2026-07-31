from rest_framework.routers import DefaultRouter
from .views import (
    AccountViewSet, JournalEntryViewSet, BudgetViewSet, SupplierViewSet,
    PurchaseRequestViewSet, PurchaseOrderViewSet, BankAccountViewSet,
    TreasuryForecastViewSet, FixedAssetViewSet, InvoiceViewSet,
)

router = DefaultRouter()
router.register("accounts", AccountViewSet, basename="account")
router.register("journal-entries", JournalEntryViewSet, basename="journal-entry")
router.register("budgets", BudgetViewSet, basename="budget")
router.register("suppliers", SupplierViewSet, basename="supplier")
router.register("purchase-requests", PurchaseRequestViewSet, basename="purchase-request")
router.register("purchase-orders", PurchaseOrderViewSet, basename="purchase-order")
router.register("bank-accounts", BankAccountViewSet, basename="bank-account")
router.register("treasury-forecasts", TreasuryForecastViewSet, basename="treasury-forecast")
router.register("fixed-assets", FixedAssetViewSet, basename="fixed-asset")
router.register("invoices", InvoiceViewSet, basename="invoice")

urlpatterns = router.urls
