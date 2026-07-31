from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import CustomTokenObtainPairSerializer


class LoginView(TokenObtainPairView):
    """POST /api/auth/login/  {email, password} -> {access, refresh, user}"""
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    """
    POST /api/auth/logout/  {refresh}
    Met le refresh token en liste noire (nécessite
    rest_framework_simplejwt.token_blacklist dans INSTALLED_APPS).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data.get("refresh", ""))
            token.blacklist()
        except TokenError:
            return Response({"detail": "Token invalide ou déjà expiré."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Déconnexion réussie."}, status=status.HTTP_205_RESET_CONTENT)
