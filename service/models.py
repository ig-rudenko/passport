import transliterate
from django.utils import timezone
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
)
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.utils.text import slugify


class Service(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=256)
    desc = models.CharField(max_length=500, null=True, blank=True)
    image = models.ImageField(upload_to="services/", null=True, blank=True)
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="private_services",
    )
    agent_token = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        db_table = "services"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if not self.slug:
            self.slug = slugify(transliterate.translit(self.name, language_code="ru", reversed=True))[:256]
        return super().save(force_insert, force_update, using, update_fields)


@receiver(pre_delete, sender=Service)
def delete_image_file(sender, instance: Service, **kwargs):
    if instance.image:
        instance.image.delete()


class UserService(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    service = models.ForeignKey("service.Service", on_delete=models.CASCADE)
    period = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(30)], null=True, blank=True
    )
    identifier = models.CharField(max_length=100)
    next_update = models.DateTimeField(default=timezone.now, null=True, blank=True)

    @property
    def private(self) -> bool:
        return self.service.user is not None

    def get_secret_values(self) -> dict:
        pass

    @property
    def get_pass_secret(self) -> str:
        return "SECRET"

    def set_secret(self, secret: dict):
        pass

    class Meta:
        db_table = "users_services"


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

    class Meta:
        db_table = "services_logs"
