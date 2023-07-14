from rest_framework import serializers

from agents.base.secret import SecretStatus, Secret
from ..models import UserService


class AgentUserServiceSerializer(serializers.ModelSerializer):
    secret = serializers.CharField(source="service.get_pass_secret", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = UserService
        fields = ["identifier", "secret", "username"]


class NewGeneratedUserServiceSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    username = serializers.CharField()
    secret = serializers.CharField()
    ok = serializers.BooleanField()
    error = serializers.CharField(max_length=500)

    def create(self, validated_data) -> SecretStatus:
        return SecretStatus(
            secret=Secret(
                identifier=validated_data["identifier"],
                username=validated_data["username"],
                secret=validated_data["secret"],
            ),
            ok=validated_data["ok"],
            error=validated_data["error"],
        )


class UserServiceSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="service.name", read_only=True)
    desc = serializers.CharField(source="service.desc", read_only=True)

    class Meta:
        model = UserService
        fields = ["service", "identifier", "period", "name", "desc"]
