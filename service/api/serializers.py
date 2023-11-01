from rest_framework import serializers

from agents.base.secret import SecretStatus, Secret
from ..models import UserService, CustomSecret


class AgentUserServiceSerializer(serializers.ModelSerializer):
    secret = serializers.CharField(source="service.secret", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = UserService
        fields = ["identifier", "secret", "username"]


class NewGeneratedUserServiceSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    username = serializers.CharField()
    secret = serializers.CharField()
    ok = serializers.BooleanField()
    error = serializers.CharField(max_length=500, allow_blank=True, allow_null=True)

    def create(self, validated_data) -> SecretStatus:
        return SecretStatus(
            secret=Secret(
                identifier=validated_data["identifier"],
                username=validated_data["username"],
                secret=validated_data["secret"],
            ),
            ok=validated_data["ok"],
            error=validated_data.get("error", None),
        )


class UserServiceListSerializer(serializers.ModelSerializer):
    """
    Для списка сервисов, которые имеют ротацию секрета
    """

    name = serializers.CharField(source="service.name", read_only=True)
    desc = serializers.CharField(source="service.desc", read_only=True)

    class Meta:
        model = UserService
        fields = ["id", "service", "identifier", "period", "name", "desc"]


class DetailUserServiceSerializer(serializers.ModelSerializer):
    """
    Для просмотра сервиса и секрета, который имеет ротацию секрета
    """

    secret = serializers.CharField(source="service.secret", read_only=True)
    name = serializers.CharField(source="service.name", read_only=True)
    desc = serializers.CharField(source="service.desc", read_only=True)

    class Meta:
        model = UserService
        fields = ["id", "secret", "service", "identifier", "period", "name", "desc"]


class UserSecretListCreateSerializer(serializers.ModelSerializer):
    """
    Для просмотра/создания списка сервисов, который создал сам пользователь
    """

    secret = serializers.CharField(write_only=True)

    class Meta:
        model = CustomSecret
        fields = ["id", "secret", "identifier", "desc"]


class DetailUserSecretSerializer(serializers.ModelSerializer):
    """
    Для просмотра/редактирования/удаления сервиса и секрета, который создал сам пользователь
    """

    secret = serializers.CharField()
    metadata = serializers.DictField(source="get_secret_metadata", read_only=True)

    class Meta:
        model = CustomSecret
        fields = ["id", "secret", "identifier", "desc", "metadata"]
