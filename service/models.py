from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MinLengthValidator,
    MinValueValidator,
    MaxValueValidator,
)
from django.db import models


class User(AbstractUser):
    telegram_id = models.IntegerField()
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


class TempCode(models.Model):
    code = models.CharField(max_length=5, validators=[MinLengthValidator(5)])
    exp = models.DateTimeField()
    service = models.ForeignKey(
        "Service", on_delete=models.CASCADE, related_name="temp_code"
    )
