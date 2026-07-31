"""
Permissions basées sur les profils utilisateurs définis dans le cahier des
charges (section 3.4 "Gestion des profils utilisateurs"):

- SUPER_ADMIN        : accès complet à tous les modules
- DG_DGA             : vue d'ensemble + validation budgets/dépenses (lecture
                        seule sur les modules métier, sauf validations)
- RH_HSSE            : module RH complet (recrutement, formation, paie, HSSE)
- COMPTABLE          : module financier complet
- RESP_OPERATIONNEL  : équipes, présences, activités, achats/maintenance
- EMPLOYE            : accès limité à ses propres données
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "SUPER_ADMIN")


class IsRHOrAbove(BasePermission):
    """Module RH: écriture pour Super Admin / RH-HSSE, lecture pour DG/DGA."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        role = request.user.role
        if role in ("SUPER_ADMIN", "RH_HSSE"):
            return True
        return request.method in SAFE_METHODS and role == "DG_DGA"


class IsComptableOrAbove(BasePermission):
    """Module financier: écriture pour Super Admin / Comptable, lecture pour DG/DGA."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        role = request.user.role
        if role in ("SUPER_ADMIN", "COMPTABLE"):
            return True
        return request.method in SAFE_METHODS and role == "DG_DGA"


class IsOperationalOrAbove(BasePermission):
    """Équipes opérationnelles (site/garage): Super Admin, RH, Resp. Opérationnel."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        role = request.user.role
        if role in ("SUPER_ADMIN", "RH_HSSE", "RESP_OPERATIONNEL"):
            return True
        return request.method in SAFE_METHODS and role == "DG_DGA"


class IsOwnerOrRHOrAbove(BasePermission):
    """
    Un employé ne voit/modifie que ses propres données (fiche, congés,
    bulletins de paie). Le RH, le Super Admin voient tout. Le DG/DGA voit
    tout en lecture seule.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        role = request.user.role
        if role in ("SUPER_ADMIN", "RH_HSSE"):
            return True
        if role == "DG_DGA" and request.method in SAFE_METHODS:
            return True
        owner = getattr(obj, "user", None) or getattr(getattr(obj, "employee", None), "user", None)
        return owner == request.user


class IsAuthenticatedReadOnly(BasePermission):
    """Utilisé pour les dashboards: lecture seule, tout utilisateur connecté."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated) and request.method in SAFE_METHODS
