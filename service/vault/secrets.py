import os

import hvac
from hvac.exceptions import InvalidPath

from .exceptions import AuthenticationError

__all__ = ['vault']


class __VaultSecrets:
    def __init__(self, vault_url, vault_token):
        # Создаем клиент для подключения к vault
        self.__client = hvac.Client(url=vault_url, token=vault_token)
        # Проверяем, что клиент авторизован и имеет доступ к секретам
        if not self.__client.is_authenticated():
            raise AuthenticationError("Неверный токен vault")
        if self.__client.sys.read_seal_status()['sealed']:
            raise AuthenticationError("Vault заблокирован")

    @property
    def client(self) -> hvac.Client:
        return self.__client

    def set_secret(self, path: str, secret_name, secret_data: dict) -> dict:
        try:
            self.__client.secrets.kv.v2.read_configuration(mount_point=path)
        except InvalidPath:
            self.__client.sys.enable_secrets_engine(backend_type="kv-v2", path=path)

        # Записываем секретные данные в виде словаря ключей и значений в vault
        return self.__client.secrets.kv.v2.create_or_update_secret(
            path=secret_name,
            secret=secret_data,
            mount_point=path
        )

    def read_secret(self, path: str, secret_name: str) -> dict:
        # Формируем путь к секрету из имени пользователя и названия секрета
        # Читаем секретные данные из vault и возвращаем их в виде словаря ключей и значений
        return self.__client.secrets.kv.v2.read_secret_version(
            path=secret_name,
            mount_point=path
        )

    def read_secret_metadata(self, path: str, secret_name: str) -> dict:
        # Формируем путь к секрету из имени пользователя и названия секрета
        # Читаем секретные данные из vault и возвращаем их в виде словаря ключей и значений
        return self.__client.secrets.kv.v2.read_secret_metadata(
            path=secret_name,
            mount_point=path
        )

    def delete_secret(self, path: str, secret_name: str):
        # Удаляем секретные данные из vault
        return self.__client.secrets.kv.v2.delete_metadata_and_all_versions(
            path=secret_name,
            mount_point=path
        )


vault = __VaultSecrets(vault_url=os.getenv("VAULT_URL"), vault_token=os.getenv("VAULT_TOKEN"))
