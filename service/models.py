from django.utils import timezone
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
)
from django.db import models
from django.contrib.auth import get_user_model
from hvac.exceptions import InvalidPath

from service.vault.secrets import vault

User = get_user_model()


class VaultSecretMixin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    identifier = models.CharField(max_length=100)

    class Meta:
        abstract = True

    @property
    def secret(self):
        try:
            secret = vault.read_secret(path=str(self.user), secret_name=self.identifier)
        except InvalidPath:
            return None
        data = secret['data']['data']
        return data.get("__secret") or data

    @secret.setter
    def secret(self, value: str | dict):
        if isinstance(value, dict):
            secret = vault
        else:
            secret = {"__secret": str(value)}

        vault.set_secret(path=str(self.user), secret_name=self.identifier, secret_data=secret)

    def get_secret_metadata(self) -> dict:
        try:
            return vault.read_secret_metadata(path=str(self.user), secret_name=self.identifier)
        except InvalidPath:
            return {}


class AgentService(models.Model):
    name = models.CharField(max_length=100)
    desc = models.CharField(max_length=500)
    agent_token = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        db_table = "agent_services"


class UserService(VaultSecretMixin):
    service = models.ForeignKey("service.AgentService", on_delete=models.CASCADE)
    period = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(30)]
    )
    next_update = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "user_services"


class CustomSecret(VaultSecretMixin):
    desc = models.CharField(max_length=500)

    class Meta:
        db_table = "custom_secrets"


class ServiceLog(models.Model):
    class Status(models.TextChoices):
        SUCCESS_VIEW = "success view", "Просмотр секрета"
        ATTEMPT_VIEW = "attempt view", "Попытка просмотра"
        SUCCESS_GENERATION = "success generation", "Успешное пересоздание"
        FAILED_GENERATION = "failed generation", "Провальное пересоздание"

    user_service = models.ForeignKey("service.UserService", on_delete=models.CASCADE, related_name="logs")
    datetime = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField(protocol="ipv4")
    status = models.CharField(choices=Status.choices, max_length=100)
    annotation = models.CharField(max_length=500)

    class Meta:
        db_table = "service_logs"
