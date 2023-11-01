from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .mocks import NotifierMock
from ..models import User, TempCode


class TestTokenAuth(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user("user1", "user1@mail.ru", "password")

    def setUp(self) -> None:
        self.client = APIClient()
        self.url = "/api/v1/account/token"
        self.data = {
            "username": "user1",
            "password": "password",
        }

    def test_auth(self):
        # Используем mock в тесте.
        with self.settings(DEFAULT_NOTIFIER_CLASS=NotifierMock):
            # Проверяем, что без кода подтверждения не получить доступ.
            response = self.client.post(self.url, self.data, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                response.data,
                {"error": "Подтвердите код, отправленный на ваш телеграм"},
            )

            # Проверяем, что имеется новый код создается в базе.
            self.assertEqual(TempCode.objects.all().count(), 1)
            temp_code: TempCode = TempCode.objects.first()

            # Проверяем что код работает.
            self.data["code"] = temp_code.code
            response = self.client.post(self.url, self.data, format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # Проверяем наличие полей access и refresh в ответе.
            self.assertIn("access", response.data)
            self.assertIn("refresh", response.data)
            # Проверяем формат токенов (должен быть JSON Web Token).
            self.assertTrue(response.data["access"].startswith("eyJh"))
            self.assertTrue(response.data["refresh"].startswith("eyJh"))

            # Проверяем, что код после использования удаляется из базы.
            self.assertEqual(TempCode.objects.all().count(), 0)
