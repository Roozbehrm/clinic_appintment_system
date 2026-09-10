import sys

from .base import BaseSMSBackend

# show sms code in console for development and testing purposes
class ConsoleBackend(BaseSMSBackend):

    def __init__(self, *args, stream=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.stream = stream or sys.stdout

    def send_message(self, phone_number, message):
        self.stream.write(f"[SMS -> {phone_number}] {message}\n")
        self.stream.flush()
        return True
