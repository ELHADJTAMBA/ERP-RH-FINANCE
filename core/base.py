"""
ViewSet de base qui journalise automatiquement chaque création / modification /
suppression dans AuditLog. Toutes les vues métier héritent de
AuditLoggingModelViewSet au lieu du ModelViewSet standard de DRF.
"""
from rest_framework.viewsets import ModelViewSet

from core.models import AuditLog
from core.pagination import StandardResultsPagination


def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class AuditLoggingModelViewSet(ModelViewSet):
    pagination_class = StandardResultsPagination

    def _log(self, action, instance):
        user = self.request.user if self.request.user.is_authenticated else None
        AuditLog.objects.create(
            user=user,
            action=action,
            model_name=instance.__class__.__name__,
            object_id=str(instance.pk),
            object_repr=str(instance)[:255],
            ip_address=_client_ip(self.request),
        )

    def perform_create(self, serializer):
        instance = serializer.save()
        self._log("CREATE", instance)

    def perform_update(self, serializer):
        instance = serializer.save()
        self._log("UPDATE", instance)

    def perform_destroy(self, instance):
        self._log("DELETE", instance)
        instance.delete()
