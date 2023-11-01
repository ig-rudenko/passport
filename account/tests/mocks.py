from account.notificator import Notifier


class NotifierMock(Notifier):
    def _notify_to_telegram(self, t_code: str, text_prefix: str = "") -> bool:
        return True

    def _notify_to_sms(self, t_code: str, text_prefix: str = "") -> bool:
        return True

