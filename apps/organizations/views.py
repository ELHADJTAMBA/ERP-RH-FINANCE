from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from core.base import AuditLoggingModelViewSet
from core.permissions import IsRHOrAbove
from .models import Site, Department
from .serializers import SiteSerializer, DepartmentSerializer


class SiteViewSet(AuditLoggingModelViewSet):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    permission_classes = [IsRHOrAbove]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["site_type", "is_active"]
    search_fields = ["name"]


class DepartmentViewSet(AuditLoggingModelViewSet):
    queryset = Department.objects.select_related("site", "manager").all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsRHOrAbove]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["site", "is_active"]
    search_fields = ["name"]
