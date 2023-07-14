from django.urls import path

from . import views

# /api/v1/account/

urlpatterns = [
    path("users/", views.UserCreateAPIView.as_view()),
    path("users/token", views.GetTokenPairView.as_view()),
]
