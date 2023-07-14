from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from account.models import User


class UserSerializer(serializers.ModelSerializer):
    telegram_id = serializers.IntegerField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "phone", "telegram_id"]
        write_only_fields = ["password", "phone"]

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)
