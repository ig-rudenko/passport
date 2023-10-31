import logging
import os
from typing import Literal

import requests


logger = logging.Logger(__file__)
logger.setLevel(logging.INFO)


class NotifierError(Exception):
    def __init__(self, msg):
        self.message = msg


class Notifier:
    __TELEGRAM_BOT_URL = f"https://api.telegram.org/bot{os.getenv('TG_TOKEN')}/"

    def __init__(self, type_: Literal["telegram", "sms"], user):
        self._type = type_
        self._user = user

    def notify(self, t_code: str, text_prefix: str = "") -> bool:
        if self._type == "telegram":
            return self._notify_to_telegram(t_code, text_prefix)
        elif self._type == "sms":
            return self._notify_to_sms(t_code, text_prefix)
        return False

    def _notify_to_telegram(self, t_code: str, text_prefix: str = "") -> bool:

        text = f"""
{text_prefix}

Код подтверждения: <b>{t_code}</b>
Никому не давайте код!

Этот код используется для подтверждения вашей личности. Он никогда не нужен для чего-либо еще.

Если Вы не запрашивали код, то вас пытаются взломать.
    """
        json_data = {
            "chat_id": self._user.telegram_id,
            "text": text.strip(),
            "parse_mode": "HTML",
        }
        resp = requests.post(
            self.__TELEGRAM_BOT_URL + "sendMessage", json=json_data, timeout=3
        )
        data = resp.json()
        if resp.status_code != 200:
            logger.error(f"notify_to_telegram {data}")
            raise NotifierError(data)
        return True

    def _notify_to_sms(self, t_code: str, text_prefix: str = "") -> bool:
        pass
