from django.db import models
from core.models import TimeStampedModel


class Site(TimeStampedModel):
    """
    Sites de l'entreprise (cahier des charges: 'Support multi-sites - Conakry,
    Site minier, Garage'). Utilisé pour catégoriser employés, présences,
    équipes, immobilisations, etc.
    """

    class SiteType(models.TextChoices):
        SIEGE = "SIEGE", "Conakry (Siège)"
        SITE_MINIER = "SITE_MINIER", "Site minier"
        GARAGE = "GARAGE", "Garage"

    name = models.CharField(max_length=150)
    site_type = models.CharField(max_length=20, choices=SiteType.choices)
    address = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_site_type_display()})"


class Department(TimeStampedModel):
    """
    Département / catégorie (cahier des charges: 'Catégorisation par
    département: Conakry, Site, Garage, Opérateurs').
    """
    name = models.CharField(max_length=150)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="departments")
    manager = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="managed_departments"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["site__name", "name"]
        unique_together = ("name", "site")

    def __str__(self):
        return f"{self.name} - {self.site.name}"
