import datetime
from django.db import models
from core.models import TimeStampedModel


def contract_file_path(instance, filename):
    return f"employees/{instance.employee.matricule}/contracts/{filename}"


class Contract(TimeStampedModel):
    """Gestion des contrats de travail (CDI, CDD, stages) + suivi des échéances."""

    class ContractType(models.TextChoices):
        CDI = "CDI", "CDI"
        CDD = "CDD", "CDD"
        STAGE = "STAGE", "Stage"

    class ContractStatus(models.TextChoices):
        ACTIVE = "ACTIVE", "Actif"
        EXPIRED = "EXPIRED", "Expiré"
        TERMINATED = "TERMINATED", "Résilié"
        RENEWED = "RENEWED", "Renouvelé"

    employee = models.ForeignKey("employees.Employee", on_delete=models.CASCADE, related_name="contracts")
    contract_type = models.CharField(max_length=10, choices=ContractType.choices)
    position = models.CharField(max_length=150)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True, help_text="Vide pour un CDI")
    base_salary = models.DecimalField(max_digits=14, decimal_places=2, help_text="Grille salariale: 2 000 000 à 15 000 000 GNF")
    status = models.CharField(max_length=15, choices=ContractStatus.choices, default=ContractStatus.ACTIVE)
    file = models.FileField(upload_to=contract_file_path, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.employee.matricule} - {self.contract_type} ({self.start_date})"

    @property
    def is_expiring_soon(self):
        """Alerte automatique: échéance dans les 30 jours (exigence 'alertes automatiques')."""
        if not self.end_date or self.status != self.ContractStatus.ACTIVE:
            return False
        return 0 <= (self.end_date - datetime.date.today()).days <= 30

    @property
    def days_until_expiry(self):
        if not self.end_date:
            return None
        return (self.end_date - datetime.date.today()).days
