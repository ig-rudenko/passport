from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import Service


class TestCreateUserServices(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/services/"
        self.user = get_user_model().objects.create_user(
            username="user1",
            email="user1@mail.ru",
            password="password",
        )
        self.service = Service.objects.create(
            name="service-name",
            agent_token="agent-token",
            desc="service description",
        )
        self.access_token = str(RefreshToken.for_user(self.user).access_token)

    def test_create_custom_service(self):
        custom_service_data = {
            "custom_service": {
                "name": "Имя сервиса",
                "desc": "Описание",
            },
            "identifier": "username",
            "secret": "secret-data",
        }

        response = self.client.post(
            path=self.url,
            data=custom_service_data,
            headers={"Authorization": f"Bearer {self.access_token}"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data,
            {
                "identifier": "username",
                "period": None,
                "name": "Имя сервиса",
                "slug": "imja-servisa",
                "desc": "Описание",
                "private": True,
                "image": None,
            },
        )

    def test_create_service_no_token(self):
        response = self.client.post(
            path=self.url,
            data={},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_user_service_from_exist_service(self):
        service_data = {
            "service": self.service.slug,
            "identifier": "username",
            "secret": "secret-data",
            "period": 7,
        }
        response = self.client.post(
            path=self.url,
            data=service_data,
            headers={"Authorization": f"Bearer {self.access_token}"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data,
            {
                "identifier": "username",
                "period": 7,
                "name": "service-name",
                "slug": "service-name",
                "desc": "service description",
                "private": False,
                "image": None,
            },
        )

    def test_invalid_create_user_service_no_period(self):
        service_data = {
            "service": self.service.slug,
            "identifier": "username",
            "secret": "secret-data",
        }
        response = self.client.post(
            path=self.url,
            data=service_data,
            headers={"Authorization": f"Bearer {self.access_token}"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(isinstance(response.data["non_field_errors"][0], ErrorDetail))

    def test_invalid_create_user_service_every_fields(self):
        service_data = {
            "custom_service": {
                "name": "Имя сервиса",
                "desc": "Описание",
            },
            "service": self.service.slug,
            "identifier": "username",
            "secret": "secret-data",
            "period": 7,
        }
        response = self.client.post(
            path=self.url,
            data=service_data,
            headers={"Authorization": f"Bearer {self.access_token}"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data,
            {
                "identifier": "username",
                "period": None,
                "name": "Имя сервиса",
                "slug": "imja-servisa",
                "desc": "Описание",
                "private": True,
                "image": None,
            },
        )
