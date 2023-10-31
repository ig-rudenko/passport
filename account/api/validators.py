from django.conf import settings
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, APIException
from rest_framework.request import Request

from account.models import TempCode
from account.notificator import NotifierError


class RequestCodeValidator:

    def __init__(self, request: Request):
        self._request = request

    def validate(self) -> bool:
        if self._request.method == "GET":
            code = self._request.query_params.get("code")
        else:
            code = self._request.data.get("code")

        if not self._request.user.is_authenticated:
            raise NotAuthenticated()

        if getattr(self._request.user, "telegram_id", None) is None:
            raise AuthenticationFailed(detail={"detail": "Для данного пользователя не был указан telegram ID"})

        if not self._request.user.temp_codes.filter(exp__gt=timezone.now()).count():
            # Если нет доступных кодов подтверждения, то создаем новый.
            notifier = settings.DEFAULT_NOTIFIER_CLASS(type_="telegram", user=self._request.user)
            try:
                notifier.notify(
                    self._request.user.generate_new_temp_code().code,
                    text_prefix=self._get_request_info(),
                )
            except NotifierError as exc:
                self._request.user.temp_codes.all().delete()
                raise APIException(detail=exc.message, code=500)
            return False

        return self._validate_code(code)

    def _get_request_info(self) -> str:
        """
        Возвращает информацию для понимания, от кого поступил запрос.
        """
        x_forwarded_for = self._request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = self._request.META.get("REMOTE_ADDR")

        return f"Запрос был получен от IP адреса: {ip}"

    @staticmethod
    def _validate_code(code: str) -> bool:
        try:
            # Если был отправлен верный код
            return TempCode.is_valid(code, raise_exception=True)
        except TempCode.InvalidCode as e:
            raise AuthenticationFailed(e.args[0])
