import logging
from functools import wraps
from typing import List

import requests

from .secret import Secret, SecretStatus

logger = logging.getLogger(__name__)

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
    def __init__(self, token: str, base_url: str):
        self._base_url = base_url
        self._session = requests.Session()
        self._session.headers = {
            "Token": token,
        }

    @handle_exception
    def check_connection(self) -> bool:
        resp = self._session.get(
            f"{self._base_url}/services/agent/check", timeout=2
        )
        if resp.status_code == 200:
            return True
        return False

    @handle_exception
    def collect_users(self) -> List[Secret]:
        resp = self._session.get(f"{self._base_url}/services/agent", timeout=2)
        if resp.status_code == 200:
            return [Secret(**data) for data in resp.json()]
        else:
            logger.error(f"collect_users status code: {resp.status_code}")
        return []

    @handle_exception
    def send_secrets(self, secrets: List[SecretStatus]) -> bool:
        data = [secret.model_dump() for secret in secrets]

        resp = self._session.post(
            f"{self._base_url}/services/agent",
            json=data,
            timeout=2,
        )
        if resp.status_code == 200:
            return True
        else:
            logger.error(f"send_secrets status code: {resp.status_code}")
            return False

    @handle_exception
    def send_status(self, status: dict) -> bool:
        resp = self._session.post(
            f"{self._base_url}/services/agent/status",
            json=status,
            timeout=2,
        )
        return resp.status_code == 200
