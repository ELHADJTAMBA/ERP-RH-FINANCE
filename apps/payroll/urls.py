from rest_framework.routers import DefaultRouter
from .views import SalaryGridViewSet, PayrollRunViewSet, PayslipViewSet

router = DefaultRouter()
router.register("salary-grids", SalaryGridViewSet, basename="salary-grid")
router.register("payroll-runs", PayrollRunViewSet, basename="payroll-run")
router.register("payslips", PayslipViewSet, basename="payslip")

urlpatterns = router.urls
