from rest_framework import generics

from service.models import UserService
from service.api.serializers import UserServiceSerializer


class ListUserServiceAPIView(generics.ListAPIView):
    serializer_class = UserServiceSerializer

    def get_queryset(self):
        return UserService.objects.filter(user=self.request.user).select_related(
            "user", "service"
        )
