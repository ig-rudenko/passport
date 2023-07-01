from functools import wraps
from typing import List

import requests

from .secret import Secret, SecretStatus


class ConnectorError(Exception):
    pass


def handle_exception(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as error:
            raise ConnectorError from error

    return wrapper


class Connector:
    def __init__(self, token: str, domain: str):
        self._domain = domain
        self._session = requests.Session()
        self._session.headers = {
            "Token": token,
        }

    @handle_exception
    def check_connection(self) -> bool:
        resp = self._session.get(
            f"{self._domain}/api/agent/service/check", timeout=2
        )
        if resp.status_code == 200:
            return True
        return False

    @handle_exception
    def collect_users(self) -> List[Secret]:
        resp = self._session.get(f"{self._domain}/api/agent/service", timeout=2)
        if resp.status_code == 200:
            return [Secret(**data) for data in resp.json()]
        return []

    @handle_exception
    def send_secrets(self, secrets: List[SecretStatus]) -> bool:
        data = [secret.model_dump() for secret in secrets]

        resp = self._session.post(
            f"{self._domain}/api/agent/service",
            json=data,
            timeout=2,
        )
        return resp.status_code == 200

    @handle_exception
    def send_status(self, status: dict) -> bool:
        resp = self._session.post(
            f"{self._domain}/api/agent/service/status",
            json=status,
            timeout=2,
        )
        return resp.status_code == 200
