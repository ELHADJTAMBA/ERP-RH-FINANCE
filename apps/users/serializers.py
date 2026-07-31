from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id", "username", "email", "first_name", "last_name",
            "phone", "role", "is_verified", "is_active", "date_joined",
        )
        read_only_fields = ("id", "is_verified", "date_joined")


class UserCreateSerializer(serializers.ModelSerializer):
    """Utilisé par le Super Admin pour créer un compte utilisateur."""
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "phone", "role", "password")

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
