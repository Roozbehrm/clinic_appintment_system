from .base import BaseSMSBackend

# exactly equivalent to the django.core.mail.outbox pattern in tests:
#     from sms.backends import locmem
#     locmem.outbox
# you can inspect the list of "sent" SMS messages.

outbox = []


class SMSMessage:
    def __init__(self, phone_number, message):
        self.phone_number = phone_number
        self.message = message

    def __repr__(self):
        return f"<SMSMessage to={self.phone_number!r} message={self.message!r}>"


class LocmemBackend(BaseSMSBackend):
    """
    not send real messages, just store them in memory for testing purposes.

        from sms.backends import locmem
        ...
        assert len(locmem.outbox) == 1
        assert locmem.outbox[0].phone_number == "09123456789"
    """

    def send_message(self, phone_number, message):
        outbox.append(SMSMessage(phone_number, message))
        return True
