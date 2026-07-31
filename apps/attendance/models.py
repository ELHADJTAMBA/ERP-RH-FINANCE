from django.db import models
from core.models import TimeStampedModel


class WorkSchedule(TimeStampedModel):
    """Gestion des horaires de travail (équipes, rotations, astreintes),
    y compris planification des équipes pour les 40 camions et le garage."""

    class ShiftType(models.TextChoices):
        DAY = "DAY", "Journée"
        NIGHT = "NIGHT", "Nuit"
        ROTATION = "ROTATION", "Rotation"
        ON_CALL = "ON_CALL", "Astreinte"

    employee = models.ForeignKey("employees.Employee", on_delete=models.CASCADE, related_name="schedules")
    shift_type = models.CharField(max_length=10, choices=ShiftType.choices)
    site = models.ForeignKey("organizations.Site", on_delete=models.CASCADE, related_name="schedules")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.employee.matricule} - {self.get_shift_type_display()} ({self.start_date})"


class Attendance(TimeStampedModel):
    """Pointage des présences (badgeuse virtuelle ou physique)."""

    class Source(models.TextChoices):
        VIRTUAL = "VIRTUAL", "Badgeuse virtuelle"
        PHYSICAL = "PHYSICAL", "Badgeuse physique"
        MANUAL = "MANUAL", "Saisie manuelle"

    class Status(models.TextChoices):
        PRESENT = "PRESENT", "Présent"
        ABSENT = "ABSENT", "Absent"
        LATE = "LATE", "En retard"
        HALF_DAY = "HALF_DAY", "Demi-journée"

    employee = models.ForeignKey("employees.Employee", on_delete=models.CASCADE, related_name="attendances")
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PRESENT)
    source = models.CharField(max_length=10, choices=Source.choices, default=Source.MANUAL)

    class Meta:
        ordering = ["-date"]
        unique_together = ("employee", "date")

    def __str__(self):
        return f"{self.employee.matricule} - {self.date} - {self.status}"

    @property
    def hours_worked(self):
        """Calcul automatique des heures travaillées (exigence C)."""
        if not (self.check_in and self.check_out):
            return None
        from datetime import datetime, date
        delta = datetime.combine(date.min, self.check_out) - datetime.combine(date.min, self.check_in)
        return round(delta.total_seconds() / 3600, 2)

    @property
    def overtime_hours(self):
        """Heures supplémentaires au-delà de 8h/jour."""
        worked = self.hours_worked
        if worked is None:
            return 0
        return round(max(0, worked - 8), 2)
