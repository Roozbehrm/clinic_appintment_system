from django.conf import settings
from django.utils.module_loading import import_string


def get_sms_connection(backend=None, fail_silently=False, **kwargs):
    """
    معادل ``django.core.mail.get_connection`` — بک‌اند مشخص‌شده در
    settings.SMS_BACKEND (یا پارامتر backend) را می‌سازد و برمی‌گرداند.
    """
    backend = backend or getattr(
        settings, "SMS_BACKEND", "sms.backends.console.ConsoleBackend"
    )
    klass = import_string(backend)
    return klass(fail_silently=fail_silently, **kwargs)


def send_sms(phone_number, message, fail_silently=False, connection=None):
    """
    نقطه‌ی ورودی اصلی برای ارسال پیامک در کل پروژه — معادل ``send_mail``.
    بسته به SMS_BACKEND در settings.py، همین یک تابع می‌تواند در توسعه
    کنسول را چاپ کند، در تست‌ها در outbox بریزد، یا در پروداکشن واقعاً
    از طریق پنل پیامکی ارسال کند؛ بدون نیاز به تغییر کد صدازننده.
    """
    connection = connection or get_sms_connection(fail_silently=fail_silently)
    return connection.send_message(phone_number, message)
