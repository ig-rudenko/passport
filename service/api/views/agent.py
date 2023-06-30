from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import NotAuthenticated

from service.models import Service, UserService, User, TempCode
from ..serializers import AgentUserServiceSerializer


class ListAgentServiceAPIView(generics.ListAPIView):
    serializer_class = AgentUserServiceSerializer
    permission_classes = [AllowAny]

    def get_service(self) -> Service:
        agent_token = self.request.META.get("HTTP_TOKEN", None)
        if agent_token is None:
            raise NotAuthenticated()

        try:
            service: Service = Service.objects.get(agent_token=agent_token)
        except Service.DoesNotExist:
            raise NotAuthenticated("Неверные данные авторизации")

        return service

    def get_queryset(self):
        service = self.get_service()
        return service.userservice_set.filter(
            user__is_active=True,
            next_update__lte=timezone.now(),
        )
