import transliterate
from rest_framework import serializers
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError

from agents.base.secret import SecretStatus, Secret
from ..models import UserService, Service


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


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ["id", "name", "slug", "desc", "agent_token", "image"]
        read_only_fields = ["id", "slug"]
        extra_kwargs = {
            "agent_token": {"write_only": True},
        }

    def create(self, validated_data) -> Service:
        # Transliterate the name to latin characters
        name = transliterate.translit(validated_data["name"], reversed=True)
        validated_data["slug"] = slugify(name)[:256]
        return super().create(validated_data)


class UserServiceSerializer(serializers.ModelSerializer):
    custom_service = ServiceSerializer(write_only=True, required=False)
    service = serializers.SlugRelatedField(
        slug_field="slug",
        write_only=True,
        required=False,
        queryset=Service.objects,
    )
    secret = serializers.CharField(write_only=True)

    private = serializers.BooleanField(read_only=True)
    name = serializers.CharField(source="service.name", read_only=True)
    slug = serializers.SlugField(source="service.slug", read_only=True)
    desc = serializers.CharField(source="service.desc", read_only=True)
    image = serializers.ImageField(source="service.image", read_only=True)

    class Meta:
        model = UserService
        fields = [
            "custom_service",
            "service",
            "identifier",
            "period",
            "secret",
            "name",
            "slug",
            "desc",
            "private",
            "image",
        ]

    def validate(self, attrs):
        custom_service = attrs.get("custom_service")
        service_slug = attrs.get("service")
        period = attrs.get("period")

        if not custom_service and not service_slug:
            raise ValidationError("Необходимо указать сервис")

        elif not custom_service and service_slug and not period:
            raise ValidationError("Необходимо указать период")

        return attrs

    def create(self, validated_data):
        if validated_data.get("custom_service"):
            custom_service = ServiceSerializer().create(
                {
                    **validated_data.pop("custom_service"),
                    "user": validated_data["user"],
                }
            )
            validated_data["service"] = custom_service

        validated_data.pop("secret")
        return super().create(validated_data)
