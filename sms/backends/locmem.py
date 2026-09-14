from .base import BaseSMSBackend

# دقیقاً معادل الگوی django.core.mail.outbox: در تست‌ها با
#     from sms.backends import locmem
#     locmem.outbox
# می‌توانید لیست پیامک‌های «ارسال‌شده» را بررسی کنید.
outbox = []


class SMSMessage:
    def __init__(self, phone_number, message):
        self.phone_number = phone_number
        self.message = message

    def __repr__(self):
        return f"<SMSMessage to={self.phone_number!r} message={self.message!r}>"


class LocmemBackend(BaseSMSBackend):
    """
    برای تست‌های خودکار (pytest/unittest): پیامک واقعی ارسال نمی‌کند، فقط
    آن را در لیست ماژول‌سطحِ ``outbox`` نگه می‌دارد تا در تست assert بزنید:

        from sms.backends import locmem
        ...
        assert len(locmem.outbox) == 1
        assert locmem.outbox[0].phone_number == "09123456789"
    """

    def send_message(self, phone_number, message):
        outbox.append(SMSMessage(phone_number, message))
        return True
