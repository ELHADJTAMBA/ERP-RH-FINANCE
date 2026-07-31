from django.db import models
from django.contrib.auth.models import AbstractUser

from .managers import CustomUserManager


class User(AbstractUser):
    """
    Utilisateur de la plateforme. `role` détermine les droits d'accès
    (voir core/permissions.py et cahier des charges §3.4).
    """

    class Role(models.TextChoices):
        SUPER_ADMIN = "SUPER_ADMIN", "Super Administrateur"
        DG_DGA = "DG_DGA", "Directeur Général / DGA"
        RH_HSSE = "RH_HSSE", "Responsable RH et HSSE"
        COMPTABLE = "COMPTABLE", "Comptable / Responsable Financier"
        RESP_OPERATIONNEL = "RESP_OPERATIONNEL", "Responsable Opérationnel"
        EMPLOYE = "EMPLOYE", "Employé"

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
