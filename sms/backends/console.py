import sys

from .base import BaseSMSBackend


class ConsoleBackend(BaseSMSBackend):
    """
    برای توسعه‌ی لوکال: به‌جای ارسال واقعی، پیامک را در کنسول/ترمینال چاپ می‌کند.
    دقیقاً معادل ``django.core.mail.backends.console.EmailBackend``.
    """

    def __init__(self, *args, stream=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.stream = stream or sys.stdout

    def send_message(self, phone_number, message):
        self.stream.write(f"[SMS -> {phone_number}] {message}\n")
        self.stream.flush()
        return True
