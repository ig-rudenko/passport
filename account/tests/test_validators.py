from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from rest_framework.exceptions import (
    NotAuthenticated,
    AuthenticationFailed,
    APIException,
)
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from account.api.validators import RequestCodeValidator
from account.models import User, TempCode
from account.tests.mocks import NotifierMock


class TestRequestCodeValidator(TestCase):
    def setUp(self):
        self.anonymous = AnonymousUser()
        self.user: User = User.objects.create_user(
            username="TestRequestCodeValidator", email="<EMAIL>", password="password"
        )
        self.factory = APIRequestFactory()
        self.request = self.factory.get("/")
        self.request = APIView().initialize_request(self.request)

        self.post_request = self.factory.post("/", data={"key": "value"})
        self.post_request = APIView().initialize_request(self.post_request)

    def test_request_anonymous_user(self):
        self.request.user = self.anonymous

        with self.settings(DEFAULT_NOTIFIER_CLASS=NotifierMock), self.assertRaises(
            NotAuthenticated
        ):
            validator = RequestCodeValidator(request=self.request)
            validator.validate()

        self.assertEqual(TempCode.objects.count(), 0)

    def test_request_user_without_tg_id(self):
        self.request.user = self.user

        with self.settings(DEFAULT_NOTIFIER_CLASS=NotifierMock), self.assertRaises(
            AuthenticationFailed
        ):
            validator = RequestCodeValidator(request=self.request)
            validator.validate()

        self.assertEqual(TempCode.objects.count(), 0)

    def test_request_user_get_method_valid_code(self):
        self.user.telegram_id = 12345
        self.request.user = self.user

        with self.settings(DEFAULT_NOTIFIER_CLASS=NotifierMock):
            validator = RequestCodeValidator(request=self.request)

            with self.assertRaises(APIException):
                validator.validate()

            self.assertEqual(TempCode.objects.count(), 1)

            code = TempCode.objects.get(user=self.user).code

            # Создаем новый запрос с переданным кодом
            request = self.factory.get(f"/?code={code}")
            request = APIView().initialize_request(request)
            request.user = self.user

            validator = RequestCodeValidator(request=request)

            # Теперь переданный код должен пройти проверку
            self.assertTrue(validator.validate())

    def test_request_user_get_method_fake_code(self):
        self.user.telegram_id = 12345
        self.request.user = self.user

        with self.settings(DEFAULT_NOTIFIER_CLASS=NotifierMock):
            validator = RequestCodeValidator(request=self.request)

            with self.assertRaises(APIException):
                validator.validate()

            self.assertEqual(TempCode.objects.count(), 1)

            # Создаем новый запрос с фальшивым кодом
            request = self.factory.get("/?code=0000")
            request = APIView().initialize_request(request)
            request.user = self.user

            # Фальшивый код не пропустит
            with self.assertRaises(AuthenticationFailed):
                RequestCodeValidator(request=request).validate()

    def test_request_user_post_method_valid_code(self):
        self.user.telegram_id = 12345
        self.post_request.user = self.user

        with self.settings(DEFAULT_NOTIFIER_CLASS=NotifierMock):
            validator = RequestCodeValidator(request=self.post_request)

            with self.assertRaises(APIException):
                validator.validate()

            self.assertEqual(TempCode.objects.count(), 1)

            code = TempCode.objects.get(user=self.user).code

            # Создаем новый запрос с переданным кодом
            post_request = self.factory.post("/", data={"code": code, "key": "value"})
            post_request = APIView().initialize_request(post_request)
            post_request.user = self.user

            validator = RequestCodeValidator(request=post_request)

            # Теперь переданный код должен пройти проверку
            self.assertTrue(validator.validate())

    def test_request_user_post_method_fake_code(self):
        self.user.telegram_id = 12345
        self.post_request.user = self.user

        with self.settings(DEFAULT_NOTIFIER_CLASS=NotifierMock):
            validator = RequestCodeValidator(request=self.post_request)

            with self.assertRaises(APIException):
                validator.validate()

            self.assertEqual(TempCode.objects.count(), 1)

            # Создаем новый запрос с фальшивым кодом
            post_request = self.factory.post("/", data={"code": "----", "key": "value"})
            post_request = APIView().initialize_request(post_request)
            post_request.user = self.user

            # Фальшивый код не пропустит
            with self.assertRaises(AuthenticationFailed):
                RequestCodeValidator(request=post_request).validate()
