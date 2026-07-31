import django.utils.timezone as tz
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response

from core.base import AuditLoggingModelViewSet
from core.permissions import IsOwnerOrRHOrAbove, IsRHOrAbove
from .models import LeaveType, LeaveRequest
from .serializers import LeaveTypeSerializer, LeaveRequestSerializer


class LeaveTypeViewSet(AuditLoggingModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [IsRHOrAbove]


class LeaveRequestViewSet(AuditLoggingModelViewSet):
    """
    Un employé crée sa propre demande (l'employee est déduit de son profil).
    RH/Super Admin valident ou rejettent via les actions dédiées.
    """
    queryset = LeaveRequest.objects.select_related("employee", "leave_type", "validated_by").all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsOwnerOrRHOrAbove]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["employee", "leave_type", "status"]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role == "EMPLOYE":
            return qs.filter(employee__user=self.request.user)
        return qs

    def perform_create(self, serializer):
        # Si l'utilisateur est un employé, on force sa propre fiche employé.
        employee = getattr(self.request.user, "employee_profile", None)
        if self.request.user.role == "EMPLOYE" and employee:
            instance = serializer.save(employee=employee)
        else:
            instance = serializer.save()
        self._log("CREATE", instance)

    @action(detail=True, methods=["post"], permission_classes=[IsRHOrAbove])
    def approve(self, request, pk=None):
        leave = self.get_object()
        leave.status = LeaveRequest.RequestStatus.APPROVED
        leave.validated_by = request.user
        leave.validated_at = tz.now()
        leave.save(update_fields=["status", "validated_by", "validated_at"])
        self._log("UPDATE", leave)
        return Response(self.get_serializer(leave).data)

    @action(detail=True, methods=["post"], permission_classes=[IsRHOrAbove])
    def reject(self, request, pk=None):
        leave = self.get_object()
        leave.status = LeaveRequest.RequestStatus.REJECTED
        leave.validated_by = request.user
        leave.validated_at = tz.now()
        leave.rejection_reason = request.data.get("rejection_reason", "")
        leave.save(update_fields=["status", "validated_by", "validated_at", "rejection_reason"])
        self._log("UPDATE", leave)
        return Response(self.get_serializer(leave).data)
