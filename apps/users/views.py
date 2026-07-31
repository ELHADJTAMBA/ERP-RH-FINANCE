from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.base import AuditLoggingModelViewSet
from core.permissions import IsSuperAdmin
from .models import User
from .serializers import UserSerializer, UserCreateSerializer, ChangePasswordSerializer


class UserViewSet(AuditLoggingModelViewSet):
    """
    Gestion des comptes utilisateurs.
    - Liste/écriture: réservé au Super Admin (création des comptes + droits).
    - `me`: tout utilisateur authentifié peut lire/modifier son propre profil.
    """
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ("me", "change_password"):
            return [IsAuthenticated()]
        return [IsSuperAdmin()]

    @action(detail=False, methods=["get", "patch"])
    def me(self, request):
        if request.method == "GET":
            return Response(UserSerializer(request.user).data)
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"old_password": "Mot de passe actuel incorrect."}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"detail": "Mot de passe mis à jour."})
