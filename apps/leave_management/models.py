from django.db import models
from core.models import TimeStampedModel


class LeaveType(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True, help_text="Ex: Congé annuel, Maladie, Permission")
    is_paid = models.BooleanField(default=True)
    max_days_per_year = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


class LeaveRequest(TimeStampedModel):
    """Suivi des absences (congés, maladie, permissions) + validation hiérarchique."""

    class RequestStatus(models.TextChoices):
        PENDING = "PENDING", "En attente"
        APPROVED = "APPROVED", "Approuvée"
        REJECTED = "REJECTED", "Rejetée"
        CANCELLED = "CANCELLED", "Annulée"

    employee = models.ForeignKey("employees.Employee", on_delete=models.CASCADE, related_name="leave_requests")
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=RequestStatus.choices, default=RequestStatus.PENDING)
    validated_by = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="validated_leaves"
    )
    validated_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.employee.matricule} - {self.leave_type.name} ({self.start_date} -> {self.end_date})"

    @property
    def days_count(self):
        """Calcul automatique du nombre de jours calendaires demandés."""
        return (self.end_date - self.start_date).days + 1
