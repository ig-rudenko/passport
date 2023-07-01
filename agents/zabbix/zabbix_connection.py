import os

from pyzabbix import ZabbixAPI
from requests import Session


class ZabbixAPIConnection:
    """Конфигурация для работы с Zabbix API"""

    url: str = os.getenv("ZABBIX_URL")
    user: str = os.getenv("ZABBIX_LOGIN")
    password: str = os.getenv("ZABBIX_PASSWORD")
    verify_session: bool = os.getenv("ZABBIX_VERIFY_SESSION") == "1"

    def __init__(self, timeout: int = 2):
        self.timeout = timeout
        self._zabbix_connection: ZabbixAPI = ZabbixAPI()
        self._session = self.get_session()

    def get_session(self) -> Session:
        session = Session()
        session.verify = self.verify_session
        return session

    def connect(self) -> ZabbixAPI:
        self._zabbix_connection = ZabbixAPI(
            server=self.url, session=self._session, timeout=self.timeout
        )
        self._zabbix_connection.login(user=self.user, password=self.password)
        return self._zabbix_connection
