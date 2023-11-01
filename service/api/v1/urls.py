from django.urls import path

from service.api.v1.views import agent, services

# /api/v1/services/

urlpatterns = [
    # Базовые сервисы
    path("", services.ListUserServicesAPIView.as_view()),
    path("<int:service_id>", services.UserServiceAPIView.as_view()),
    # Пользовательские сервисы
    path("secret", services.ListCreateUserSecretAPIView.as_view()),
    path("secret/<int:secret_id>", services.UserSecretAPIView.as_view()),
    # Для агентов
    path("agent", agent.ListAgentServiceAPIView.as_view()),
    path("agent/check", agent.CheckAgentAPIView.as_view()),
]
