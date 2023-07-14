import logging

from urllib3.exceptions import NewConnectionError
from pyzabbix import ZabbixAPIException
from ..base.generator import BaseGenerator
from ..base.secret import Secret, SecretStatus
from .zabbix_connection import ZabbixAPIConnection

logger = logging.getLogger(__name__)


class ZabbixGenerator(BaseGenerator):
    def regenerate(self, old_secret: Secret) -> SecretStatus:
        new_password = self.generate_secret(length=8, symbols=False)
        new_secret = Secret(
            username=old_secret.username,
            identifier=old_secret.identifier,
            secret=new_password,
        )
        try:
            self._send_to_zabbix(new_secret)
            return SecretStatus(secret=new_secret, ok=True)
        except Exception as error:
            error_message = self._get_exception_message(error)
        return SecretStatus(secret=old_secret, ok=False, error=error_message)

    @staticmethod
    def _send_to_zabbix(new_secret: Secret) -> None:
        with ZabbixAPIConnection().connect() as zbx:
            user = zbx.user.get(
                filter={"alias": new_secret.username},
                output=["userid"],
            )
            if user:
                user_id = user[0]["userid"]
                zbx.user.update(userid=user_id, passwd=new_secret.secret)
                logger.debug(f"create new secret for {new_secret.username}")
                return
        raise ZabbixAPIException(
            error={
                "data": f'Пользователь под username "{new_secret.username}" не существует,'
                " либо агент не имеет доступа к его изменению"
            }
        )

    @staticmethod
    def _get_exception_message(error: Exception) -> str:
        logger.error(error, exc_info=True)

        if isinstance(error, ZabbixAPIException):
            return str(error.error.get("data"))
        elif isinstance(error, NewConnectionError):
            if error.args:
                return str(error.args[0].reason).split(": ")[-1]
        else:
            return str(error)
