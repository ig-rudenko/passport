from rest_framework import generics

from service.models import UserService
from ..serializers import UserServiceSerializer


class ListCreateUserServiceAPIView(generics.ListCreateAPIView):
    serializer_class = UserServiceSerializer

    def get_queryset(self):
        return UserService.objects.filter(user=self.request.user).select_related(
            "user", "service"
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
