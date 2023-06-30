from rest_framework import serializers

from ..models import UserService


class AgentUserServiceSerializer(serializers.ModelSerializer):
    secret = serializers.CharField(source="service.get_pass_secret", read_only=True)

    class Meta:
        model = UserService
        fields = ["identifier", "secret"]


class UserServiceSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="service.name", read_only=True)
    desc = serializers.CharField(source="service.desc", read_only=True)

    class Meta:
        model = UserService
        fields = ["service", "identifier", "period", "name", "desc"]
