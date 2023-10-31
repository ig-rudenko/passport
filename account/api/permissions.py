from django.conf import settings
from django.utils import timezone
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from account.models import TempCode


class CodePermission(BasePermission):
    notificator_class = settings.DEFAULT_NOTIFIER_CLASS

    def has_permission(self, request: Request, view: APIView) -> bool:

        if request.method == "GET":
            code = request.query_params.get("code")
        else:
            code = request.data.get("code")

        if not request.user.is_authenticated:
            raise NotAuthenticated()

        if not request.user.temp_codes.filter(exp__gt=timezone.now()).count():
            # Если нет доступных кодов подтверждения, то создаем новый.
            notifier = self.notificator_class(type_="telegram", user=request.user)
            notifier.notify(
                request.user.generate_new_temp_code().code,
                text_prefix=self.get_request_info(request),
            )
            return False

        return self.validate_code(code)

    @staticmethod
    def get_request_info(request: Request) -> str:
        """
        Возвращает информацию для понимания, от кого поступил запрос.
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")

        return f"Запрос был получен от IP адреса: {ip}"

    @staticmethod
    def validate_code(code: str) -> bool:
        try:
            # Если был отправлен верный код
            return TempCode.is_valid(code, raise_exception=True)
        except TempCode.InvalidCode as e:
            raise AuthenticationFailed(e.args[0])

    @property
    def message(self) -> str:
        return "Подтвердите код, отправленный на ваш телеграм/sms"
