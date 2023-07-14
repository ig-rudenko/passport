from rest_framework import generics

from ..serializers import UserSerializer
from account.models import User


class UserCreateAPIView(generics.CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
