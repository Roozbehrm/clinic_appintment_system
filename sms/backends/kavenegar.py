import requests
from django.conf import settings

from .base import BaseSMSBackend


class KavenegarBackend(BaseSMSBackend):
    """
    بک‌اند نمونه برای درگاه پیامک Kavenegar (kavenegar.com) — یکی از
    پرکاربردترین پنل‌های پیامکی ایران. برای پنل دیگری (ملی‌پیامک، فراز
    اس‌ام‌اس و ...) کافی است یک فایل مشابه با متد send_message متناسب با
    API همان سرویس بسازید و SMS_BACKEND را به آن اشاره دهید — کد بقیه‌ی
    پروژه (issue_otp، ویوها و ...) دست‌نخورده می‌ماند.
    """

    API_URL = "https://api.kavenegar.com/v1/{api_key}/sms/send.json"

    def send_message(self, phone_number, message):
        api_key = getattr(settings, "SMS_API_KEY", "")
        sender = getattr(settings, "SMS_SENDER_LINE", "")

        if not api_key:
            if self.fail_silently:
                return False
            raise ValueError(
                "SMS_API_KEY تنظیم نشده است. مقدارش را در .env قرار دهید."
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
