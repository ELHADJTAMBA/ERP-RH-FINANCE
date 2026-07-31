import datetime
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response

from core.base import AuditLoggingModelViewSet
from core.permissions import IsOwnerOrRHOrAbove
from .models import Contract
from .serializers import ContractSerializer


class ContractViewSet(AuditLoggingModelViewSet):
    queryset = Contract.objects.select_related("employee").all()
    serializer_class = ContractSerializer
    permission_classes = [IsOwnerOrRHOrAbove]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["employee", "contract_type", "status"]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role == "EMPLOYE":
            return qs.filter(employee__user=self.request.user)
        return qs

    @action(detail=False, methods=["get"])
    def expiring_soon(self, request):
        """GET /api/contracts/expiring_soon/ -> contrats arrivant à échéance sous 30 jours."""
        limit = datetime.date.today() + datetime.timedelta(days=30)
        qs = self.get_queryset().filter(
            status=Contract.ContractStatus.ACTIVE,
            end_date__isnull=False,
            end_date__lte=limit,
            end_date__gte=datetime.date.today(),
        )
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
