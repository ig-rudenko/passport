from django.urls import path
from service.api.v1.views import agent, services

# /api/v1/services/

urlpatterns = [
    path("", services.ListCreateUserServiceAPIView.as_view()),
    path("agent", agent.ListAgentServiceAPIView.as_view()),
    path("agent/check", agent.CheckAgentAPIView.as_view()),
]
