import logging

import requests
from django.conf import settings

logger = logging.Logger(__file__)
logger.setLevel(logging.INFO)


def notify_to_telegram(tg_id: int, t_code: str, text_prefix: str = "") -> bool:

    text = f"""
{text_prefix}

Код подтверждения: <code>{t_code}</code>
Никому не давайте код!

Этот код используется для подтверждения вашей личности. Он никогда не нужен для чего-либо еще.

Если Вы не запрашивали код для входа, то вас пытаются взломать.
"""
    json_data = {"chat_id": tg_id, "text": text.strip(), "parse_mode": "HTML"}
    resp = requests.post(
        settings.TELEGRAM_BOT_URL + "sendMessage", json=json_data, timeout=3
    )
    logger.info(resp.json())
    return resp.status_code == 200
