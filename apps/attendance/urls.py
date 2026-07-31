from rest_framework.routers import DefaultRouter
from .views import WorkScheduleViewSet, AttendanceViewSet

router = DefaultRouter()
router.register("work-schedules", WorkScheduleViewSet, basename="work-schedule")
router.register("attendances", AttendanceViewSet, basename="attendance")

urlpatterns = router.urls
