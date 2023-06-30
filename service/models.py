import string
import secrets
from datetime import timedelta

from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MinLengthValidator,
    MinValueValidator,
    MaxValueValidator,
)
from django.db import models


class User(AbstractUser):
    telegram_id = models.IntegerField(null=True, blank=True)
    phone = models.CharField(
        validators=[MinLengthValidator(11)], max_length=11, null=True, blank=True
    )
    services = models.ManyToManyField(
        "Service", through="UserService", related_name="users_set"
    )


class UserService(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    service = models.ForeignKey("Service", on_delete=models.CASCADE)
    period = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(30)]
    )
    identifier = models.CharField(max_length=100)
    next_update = models.DateTimeField(default=timezone.now)


class Service(models.Model):
    name = models.CharField(max_length=100)
    desc = models.CharField(max_length=500)
    user = models.ForeignKey(
        "User",
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


class TempCode(models.Model):
    code = models.CharField(max_length=5, validators=[MinLengthValidator(5)])
    exp = models.DateTimeField()
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    service = models.ForeignKey(
        "Service", on_delete=models.CASCADE, related_name="temp_code"
    )

    @staticmethod
    def get_service_from_code(code: str, user: User) -> Service:
        temp_code = get_object_or_404(TempCode, code=code.upper(), user=user)
        if temp_code.exp < timezone.now():
            raise TempCode.InvalidCode("Код был просрочен")
        return temp_code.service

    @classmethod
    def generate_new(
        cls, user: User, service: Service, timedelta_=timedelta(minutes=1)
    ) -> "TempCode":
        """
        Функция генерирует временный код, состоящий из случайных символов алфавита, со сроком действия,
        основанным на текущем времени плюс заданная временная дельта для данной услуги.
        :return: экземпляр класса "TempCode".
        """

        # Удаляем старые коды
        TempCode.objects.filter(service=service, user=user).delete()

        alphabet = string.ascii_uppercase + string.digits
        return TempCode(
            code="".join(secrets.choice(alphabet) for _ in range(5)),
            exp=timezone.now() + timedelta_,
            user=user,
            service=service,
        )

    class InvalidCode(Exception):
        pass
