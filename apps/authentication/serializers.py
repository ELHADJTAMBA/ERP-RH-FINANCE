from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.users.serializers import UserSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Login par email (USERNAME_FIELD) + mot de passe. Ajoute le rôle dans le
    payload du JWT et renvoie les infos utilisateur dans la réponse, pour que
    le frontend puisse adapter l'interface (menus) sans appel supplémentaire.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["email"] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data
