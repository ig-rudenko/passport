from django.utils import timezone
from django.conf import settings
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.views import TokenObtainPairView

from account.models import User, TempCode
from .swagger.schemas import obtain_token_schema
from .serializers import UserSerializer, NewTokenObtainPairSerializer


class UserCreateAPIView(generics.CreateAPIView):
    """
    # Регистрация нового пользователя
    """

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny]


class GetTokenPairView(TokenObtainPairView):
    serializer_class = NewTokenObtainPairSerializer
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
        return serializer

    @obtain_token_schema
    def post(self, request, *args, **kwargs):
        """
        # Создает пару JWT - access и refresh.
        Но только в том случае, когда передается верный код для подтверждения.
        Если код отсутствует в запросе и у пользователя не было ни одного ранее отправленного кода,
        тогда будет случайно сгенерирован буквенно-цифровой код и отправлен через телеграм бота пользователю,
        данные которого передаются в запросе.
        """
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

        self.validate_code(code, user)

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
    def validate_code(code: str, user):
        try:
            # Если был отправлен верный код
            TempCode.is_valid(code, user, raise_exception=True)
        except TempCode.InvalidCode as e:
            raise AuthenticationFailed(e.args[0])
