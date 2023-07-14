from django.utils import timezone
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import NotAuthenticated

from service.models import Service, UserService
from service.api.serializers import AgentUserServiceSerializer, NewGeneratedUserServiceSerializer


class AgentMixin:
    def get_service(self) -> Service:
        agent_token = self.request.META.get("HTTP_TOKEN", None)
        if agent_token is None:
            raise NotAuthenticated("Token не был предоставлен")

        try:
            service: Service = Service.objects.get(agent_token=agent_token)
        except Service.DoesNotExist:
            raise NotAuthenticated("Неверные данные авторизации")

        return service


class CheckAgentAPIView(generics.GenericAPIView, AgentMixin):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        if self.get_service():
            return Response()


class ListAgentServiceAPIView(generics.ListAPIView, AgentMixin):
    permission_classes = [AllowAny]
    serializer_class = AgentUserServiceSerializer

    def get_queryset(self):
        service = self.get_service()
        return service.userservice_set.filter(
            user__is_active=True,
            next_update__lte=timezone.now(),
        )

    def post(self, request, *args, **kwargs):
        service = self.get_service()

        serializer = NewGeneratedUserServiceSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        secret_status_list = serializer.save()

        for secret_status in secret_status_list:
            if not secret_status.ok:
                print(secret_status.error)

            if UserService.objects.filter(
                service=service,
                user__username=secret_status.secret.username,
                identifier=secret_status.secret.identifier,
            ).exists():
                pass
                # set_new_secret(secret_status.secret)

        return Response(serializer.validated_data)
