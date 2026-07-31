from rest_framework.routers import DefaultRouter
from .views import SiteViewSet, DepartmentViewSet

router = DefaultRouter()
router.register("sites", SiteViewSet, basename="site")
router.register("departments", DepartmentViewSet, basename="department")

urlpatterns = router.urls
