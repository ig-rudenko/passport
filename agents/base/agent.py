import time
import logging
from typing import List

from .generator import BaseGenerator, GeneratorException
from .secret import Secret, SecretStatus
from .connector import Connector, ConnectorError

logger = logging.getLogger(__name__)


class Agent:
    def __init__(self, connector: Connector, generator: BaseGenerator):
        self.connector = connector
        self.generator = generator
        self._old_secrets: List[Secret] = []
        self._new_secrets: List[SecretStatus] = []

    def start(self):
        """
        Основной цикл работы агента
        """
        while True:
            try:
                self.get_refresh_list()
                logger.info(f"get {len(self._old_secrets)} secrets")
                try:
                    self.regenerate_secrets()
                    logger.info(f"regenerate {len(self._old_secrets)} secrets")
                except GeneratorException as err:
                    self.connector.send_status({"error": err.message})
                    logger.error(err.message, exc_info=True)
                else:
                    self.send_new_secrets()
                finally:
                    self._clear()
            except Exception as error:
                logger.error(error, exc_info=True)
            finally:
                time.sleep(60)

    def get_refresh_list(self):
        self._old_secrets = self.connector.collect_users()

    def regenerate_secrets(self):
        for secret in self._old_secrets:
            new_secret_status: SecretStatus = self.generator.regenerate(secret)
            self._new_secrets.append(new_secret_status)

    def send_new_secrets(self):
        if self._new_secrets:
            self.connector.send_secrets(self._new_secrets)

    def _clear(self):
        self._old_secrets = []
        self._new_secrets = []
