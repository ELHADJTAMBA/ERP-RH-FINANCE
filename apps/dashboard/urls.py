from django.urls import path
from .views import (
    HRDashboardView, FinanceDashboardView, OperationsDashboardView, HSSEDashboardView,
)

urlpatterns = [
    path("dashboard/hr/", HRDashboardView.as_view(), name="dashboard-hr"),
    path("dashboard/finance/", FinanceDashboardView.as_view(), name="dashboard-finance"),
    path("dashboard/operations/", OperationsDashboardView.as_view(), name="dashboard-operations"),
    path("dashboard/hsse/", HSSEDashboardView.as_view(), name="dashboard-hsse"),
]
