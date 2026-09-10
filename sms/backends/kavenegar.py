import requests
from django.conf import settings

from .base import BaseSMSBackend

# change this name to your backend name, e.g. "mellipayamak"
class KavenegarBackend(BaseSMSBackend):


    API_URL = "https://api.kavenegar.com/v1/{api_key}/sms/send.json"

    def send_message(self, phone_number, message):
        api_key = getattr(settings, "SMS_API_KEY", "")
        sender = getattr(settings, "SMS_SENDER_LINE", "")

        if not api_key:
            if self.fail_silently:
                return False
            raise ValueError(
                "sms api key is not set. Please set SMS_API_KEY in your .env file"
            )

        try:
            response = requests.post(
                self.API_URL.format(api_key=api_key),
                data={"receptor": phone_number, "sender": sender, "message": message},
                timeout=10,
            )
            response.raise_for_status()
            return True
        except requests.RequestException:
            if self.fail_silently:
                return False
            raise
