from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from . import views

# /api/v1/account/

urlpatterns = [
    path("users/", views.UserCreateAPIView.as_view()),
    path("token", views.GetTokenPairView.as_view()),
    path("token/refresh", TokenRefreshView.as_view()),
    path("token/verify", TokenVerifyView.as_view()),
]
