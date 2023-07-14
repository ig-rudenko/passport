from django.utils import timezone
from django.conf import settings
from rest_framework import generics, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from ..serializers import UserSerializer
from account.models import User, TempCode


class UserCreateAPIView(generics.CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()


class GetTokenPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer
    notificator_class = settings.DEFAULT_NOTIFIER_CLASS

    def get_validate_serializer(self):
        """
        Возвращает проверенный объект сериализатора.
        """
        serializer = self.get_serializer(data=self.request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        finally:
            return serializer

    def post(self, request, *args, **kwargs):
        code = request.data.get("code")
        serializer = self.get_validate_serializer()

        user: User = serializer.user

        if not user.temp_codes.filter(exp__gt=timezone.now()).count():
            # Если нет доступных кодов подтверждения, то создаем новый.
            notifier = self.notificator_class(type_="telegram", user=user)
            notifier.notify(
                user.generate_new_temp_code().code,
                text_prefix=self.get_request_info(),
            )
            return Response(
                {"error": "Подтвердите код, отправленный на ваш телеграм"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.validate_code(code)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    def get_request_info(self) -> str:
        """
        Возвращает информацию для понимания, от кого поступил запрос.
        """
        x_forwarded_for = self.request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = self.request.META.get("REMOTE_ADDR")

        return f"Запрос был получен от IP адреса: {ip}"

    @staticmethod
    def validate_code(code: str):
        try:
            # Если был отправлен верный код
            TempCode.is_valid(code, raise_exception=True)
        except TempCode.InvalidCode as e:
            raise AuthenticationFailed(e.args[0])
