from django.conf import settings
from melipayamak import Api
from .base import BaseSMSBackend

# ======================================================================
# بک‌اند اختصاصی برای ارسال پیامک از طریق درگاه ملی پیامک
# ======================================================================
class MelliPayamakBackend(BaseSMSBackend):
    """
    برای استفاده از این درگاه، متغیرهای زیر باید در settings.py 
    (و در نهایت از فایل .env) خوانده شوند:
    SMS_USERNAME = "..."
    SMS_PASSWORD = "..."
    SMS_SENDER_LINE = "..."
    """

    def send_message(self, phone_number, message):
        # خواندن اطلاعات از فایل تنظیمات پروژه
        username = getattr(settings, "SMS_USERNAME", "")
        password = getattr(settings, "SMS_PASSWORD", "")
        sender = getattr(settings, "SMS_SENDER_LINE", "")

        if not username or not password or not sender:
            if self.fail_silently:
                return False
            raise ValueError(
                "تنظیمات ملی پیامک (SMS_USERNAME, SMS_PASSWORD, SMS_SENDER_LINE) در تنظیمات وارد نشده است."
            )

        try:
            # ارتباط با API ملی پیامک
            api = Api(username, password)
            sms = api.sms()
            to = str(phone_number).strip()

            # ارسال پیامک
            response = sms.send(to, sender, message)

            # بررسی وضعیت ارسال
            if isinstance(response, dict) and response.get("RetStatus") == 1:
                return True
            else:
                if self.fail_silently:
                    return False
                raise Exception(f"خطای ملی پیامک: {response}")

        except Exception as e:
            if self.fail_silently:
                return False
            # در صورتی که fail_silently فالس باشه، ارور اصلی رو بالا میندازیم
            raise