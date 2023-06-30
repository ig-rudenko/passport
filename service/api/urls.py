from django.urls import path
from .views import services
from .views import agent

# /api/

urlpatterns = [
    path("services", services.ListUserServiceAPIView.as_view()),
    path("agent/service", agent.ListAgentServiceAPIView.as_view()),
]
