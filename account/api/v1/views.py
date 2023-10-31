from django.conf import settings
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from ..serializers import UserSerializer
from account.models import User
from ..validators import RequestCodeValidator


class UserCreateAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
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

        return serializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.get_validate_serializer()
        request.user = serializer.user

        RequestCodeValidator(request).validate()

        return Response(serializer.validated_data, status=status.HTTP_200_OK)
