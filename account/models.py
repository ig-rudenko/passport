from datetime import timedelta

from django.core.validators import MinLengthValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

from .code_generator import generate_code


class User(AbstractUser):
    telegram_id = models.IntegerField(null=True, blank=True)
    phone = models.CharField(
        validators=[MinLengthValidator(11)], max_length=11, null=True, blank=True
    )
    services = models.ManyToManyField(
        "service.Service", through="service.UserService", related_name="users_set"
    )

    def __str__(self):
        return self.username

    class Meta:
        db_table = "users"

    def generate_new_temp_code(self, timedelta_=timedelta(minutes=1)) -> "TempCode":
        """
        Функция генерирует новый временный код, состоящий из случайных символов алфавита, со сроком действия,
        основанным на текущем времени плюс заданная временная дельта для данной услуги.
        :return: экземпляр класса "TempCode".
        """

        # Удаляем старые коды
        TempCode.objects.filter(user_id=self.id).delete()

        return TempCode(
            code=generate_code(5),
            exp=timezone.now() + timedelta_,
            user_id=self.id,
        )


class TempCode(models.Model):
    code = models.CharField(max_length=5, validators=[MinLengthValidator(5)])
    exp = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="temp_codes")

    @staticmethod
    def is_valid(code: str, raise_exception=False) -> bool:
        try:
            t_code = TempCode.objects.get(code=code)
        except TempCode.DoesNotExist:
            if raise_exception:
                raise TempCode.InvalidCode("Код подтверждения неверный или устарел")
            else:
                return False

        if t_code.exp < timezone.now():
            t_code.delete()
            if raise_exception:
                raise TempCode.InvalidCode("Код был просрочен")
            else:
                return False
        return True

    class InvalidCode(Exception):
        pass

    class Meta:
        db_table = "temp_codes"
