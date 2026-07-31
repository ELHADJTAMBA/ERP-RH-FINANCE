from rest_framework.routers import DefaultRouter
from .views import LeaveTypeViewSet, LeaveRequestViewSet

router = DefaultRouter()
router.register("leave-types", LeaveTypeViewSet, basename="leave-type")
router.register("leave-requests", LeaveRequestViewSet, basename="leave-request")

urlpatterns = router.urls
