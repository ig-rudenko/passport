from rest_framework import generics

from service.models import Service, UserService, User, TempCode
from ..serializers import UserServiceSerializer


class ListUserServiceAPIView(generics.ListAPIView):
    serializer_class = UserServiceSerializer

    def get_queryset(self):
        return UserService.objects.filter(user=self.request.user).select_related("user", "service")
