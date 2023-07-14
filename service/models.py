from django.utils import timezone
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
)
from django.db import models
from django.contrib.auth import get_user_model


class Service(models.Model):
    name = models.CharField(max_length=100)
    desc = models.CharField(max_length=500)
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="private_services",
    )
    agent_token = models.CharField(max_length=256, blank=True, null=True)

    @property
    def private(self) -> bool:
        return self.user is not None

    def get_secret_values(self) -> dict:
        pass

    @property
    def get_pass_secret(self) -> str:
        return "SECRET"

    def set_secret(self, secret: dict):
        pass


class UserService(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    service = models.ForeignKey("service.Service", on_delete=models.CASCADE)
    period = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(30)]
    )
    identifier = models.CharField(max_length=100)
    next_update = models.DateTimeField(default=timezone.now)


class ServiceLog(models.Model):
    class Status(models.TextChoices):
        SUCCESS_VIEW = "SV", "Просмотр секрета"
        ATTEMPT_VIEW = "AV", "Попытка просмотра"
        SUCCESS_GENERATION = "SG", "Успешное пересоздание"
        FAILED_GENERATION = "FG", "Провальное пересоздание"

    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="logs"
    )
    service = models.ForeignKey(
        "service.Service", on_delete=models.CASCADE, related_name="logs"
    )
    ip = models.GenericIPAddressField(protocol="ipv4")
    status = models.CharField(choices=Status.choices, max_length=2)
    annotation = models.CharField(max_length=500)
