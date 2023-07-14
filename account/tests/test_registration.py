from django.test import TestCase
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient


class TestRegistration(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.url = "/api/v1/account/users"
        self.valid_data = {
            "username": "user1",
            "email": "user1@mail.ru",
            "password": "password",
            "telegram_id": 1234567890,
            "phone": "79789789797",
        }
        self.without_tg_id_data = {
            "username": "user1",
            "email": "user1@mail.ru",
            "password": "password",
            "phone": "79789789797",
        }
        self.no_password_data = {
            "username": "user1",
            "email": "user1@mail.ru",
            "password": "",
            "telegram_id": 1234567890,
        }
        self.empty_data = {}

    def test_user_registration(self):
        data = self.valid_data
        response = self.client.post(self.url, data, format="json")
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertIsNone(response.data.get("password"))
        self.assertTrue("id" in response.data)
        self.assertEqual(response.data["username"], data["username"])
        self.assertEqual(response.data["telegram_id"], data["telegram_id"])
        self.assertEqual(response.data["email"], data["email"])
        self.assertEqual(response.data["phone"], data["phone"])

    def test_user_registration_without_tg_id(self):
        data = self.without_tg_id_data
        response = self.client.post(self.url, data, format="json")
        print(response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIsNone(response.data.get("password"))
        self.assertIsNone(response.data.get("id"))
        self.assertTrue(isinstance(response.data["telegram_id"][0], ErrorDetail))

    def test_user_registration_no_password(self):
        data = self.no_password_data
        response = self.client.post(self.url, data, format="json")
        print(response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIsNone(response.data.get("id"))
        self.assertTrue(isinstance(response.data["password"][0], ErrorDetail))

    def test_user_registration_empty_data(self):
        data = self.empty_data
        response = self.client.post(self.url, data, format="json")
        print(response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIsNone(response.data.get("id"))
        self.assertTrue(isinstance(response.data["username"][0], ErrorDetail))
        self.assertTrue(isinstance(response.data["email"][0], ErrorDetail))
        self.assertTrue(isinstance(response.data["password"][0], ErrorDetail))
        self.assertTrue(isinstance(response.data["telegram_id"][0], ErrorDetail))
