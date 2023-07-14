from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from account.models import User, TempCode
from ..serializers import UserSerializer
from ...notificator import notify_to_telegram


class UserCreateAPIView(generics.CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()


class NewTokenObtainPairSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None


class GetTokenPairView(TokenObtainPairView):
    serializer_class = NewTokenObtainPairSerializer

    def get_validate_serializer(self):
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
            # Если нет доступных кодов подтверждения.
            notify_to_telegram(user.telegram_id, user.generate_new_temp_code().code)
            return Response(
                {"error": "Подтвердите код, отправленный на ваш телеграм"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.validate_code(code)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    @staticmethod
    def validate_code(code: str):
        try:
            # Если был отправлен верный код
            TempCode.is_valid(code, raise_exception=True)
        except TempCode.InvalidCode as e:
            raise AuthenticationFailed(e.args[0])
