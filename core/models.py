from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    """Ajoute created_at / updated_at à tout modèle qui en hérite."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AuditLog(models.Model):
    """
    Traçabilité de toutes les actions (exigence 3.3 Sécurité: 'logs d'audit').
    Créé automatiquement par core.base.AuditLoggingModelViewSet à chaque
    create/update/delete effectué via l'API.
    """
    ACTION_CHOICES = (
        ("CREATE", "Création"),
        ("UPDATE", "Modification"),
        ("DELETE", "Suppression"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="audit_logs"
    )
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=50)
    object_repr = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["model_name", "object_id"]),
            models.Index(fields=["user", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.timestamp:%Y-%m-%d %H:%M} - {self.user} - {self.action} - {self.model_name}#{self.object_id}"
