import requests
from django.conf import settings


def notify_to_telegram(tg_id: int, t_code: str, text_prefix: str = ""):
    if text_prefix:
        text_prefix += "\n"

    text = f"{text_prefix}Код: `{t_code}`"
    json_data = {"chat_id": tg_id, "text": text}
    requests.post(settings.TELEGRAM_BOT_URL + "sendMessage", json=json_data, timeout=2)
