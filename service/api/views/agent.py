from datetime import timedelta

from django.db.models.query import F
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import AllowAny

from service.models import Service, UserService, User, TempCode
from ..serializers import UserServiceSerializer, AgentUserServiceSerializer


class ListAgentServiceAPIView(generics.ListAPIView):
    serializer_class = AgentUserServiceSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        agent_token = self.request.META.get("HTTP_TOKEN")
        return get_object_or_404(
            Service, agent_token=agent_token
        ).userservice_set.filter(
            user__is_active=True,
            next_update__lte=timezone.now(),
        )
