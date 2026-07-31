from django_filters.rest_framework import DjangoFilterBackend

from core.base import AuditLoggingModelViewSet
from core.permissions import IsOperationalOrAbove, IsOwnerOrRHOrAbove
from .models import WorkSchedule, Attendance
from .serializers import WorkScheduleSerializer, AttendanceSerializer


class WorkScheduleViewSet(AuditLoggingModelViewSet):
    queryset = WorkSchedule.objects.select_related("employee", "site").all()
    serializer_class = WorkScheduleSerializer
    permission_classes = [IsOperationalOrAbove]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["employee", "site", "shift_type"]


class AttendanceViewSet(AuditLoggingModelViewSet):
    queryset = Attendance.objects.select_related("employee").all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsOwnerOrRHOrAbove]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["employee", "date", "status"]

    def get_queryset(self):
        qs = super().get_queryset()
        role = self.request.user.role
        if role == "EMPLOYE":
            return qs.filter(employee__user=self.request.user)
        if role == "RESP_OPERATIONNEL":
            return qs.filter(employee__site__in=[
                d.site for d in self.request.user.managed_departments.all()
            ]) if self.request.user.managed_departments.exists() else qs
        return qs
