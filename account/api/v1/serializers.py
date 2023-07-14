from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from account.models import User


class UserSerializer(serializers.ModelSerializer):
    telegram_id = serializers.IntegerField(required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "phone", "telegram_id"]
        write_only_fields = ["password", "phone"]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)


class NewTokenObtainPairSerializer(TokenObtainPairSerializer):
    code = serializers.CharField(write_only=True, default="", allow_blank=True)
