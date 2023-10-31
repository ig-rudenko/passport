from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from account.api.permissions import CodePermission
from service.models import UserService, CustomSecret
from service.api.serializers import UserServiceListSerializer, DetailUserServiceSerializer, \
    UserSecretListCreateSerializer, \
    DetailUserSecretSerializer


class ListServicesAPIView(generics.ListAPIView):
    serializer_class = UserServiceListSerializer
    queryset = UserService.objects.all()


class ListUserServicesAPIView(generics.ListAPIView):
    """
    API Для просмотра списка сервисов, которые имеют ротацию секрета
    """
    serializer_class = UserServiceListSerializer

    def get_queryset(self):
        return UserService.objects.filter(user=self.request.user).select_related("user", "service")


class UserServiceAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API Для просмотра/редактирования/удаления секрета сервиса, который имеет ротацию секрета
    """
    serializer_class = DetailUserServiceSerializer
    lookup_url_kwarg = "service_id"
    permission_classes = [IsAuthenticated, CodePermission]

    def get_queryset(self):
        return UserService.objects.filter(user=self.request.user).select_related("user", "service")


class ListUserCustomServicesAPIView(generics.ListCreateAPIView):
    """
    API Для просмотра списка сервисов, который создал сам пользователь
    """
    serializer_class = UserSecretListCreateSerializer

    def get_queryset(self):
        return CustomSecret.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CustomUserServiceAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API Для просмотра/редактирования/удаления секрета сервиса, который создал сам пользователь
    """
    serializer_class = DetailUserSecretSerializer
    lookup_url_kwarg = "service_id"
    permission_classes = [IsAuthenticated, CodePermission]

    def get_queryset(self):
        return CustomSecret.objects.filter(user=self.request.user)
