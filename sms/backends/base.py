class BaseSMSBackend:
    """
    کلاس پایه برای بک‌اندهای پیامک — دقیقاً مشابه الگوی
    ``django.core.mail.backends.base.BaseEmailBackend``.

    برای اضافه‌کردن یک درگاه پیامک واقعی، از این کلاس ارث‌بری کنید و
    متد ``send_message`` را پیاده‌سازی کنید.
    """

    def __init__(self, fail_silently=False, **kwargs):
        self.fail_silently = fail_silently

    def open(self):
        """اتصال به سرویس را برقرار می‌کند (در صورت نیاز). پیش‌فرض کاری نمی‌کند."""
        return False

    def close(self):
        """اتصال را می‌بندد (در صورت نیاز). پیش‌فرض کاری نمی‌کند."""
        pass

    def send_message(self, phone_number, message):
        """
        یک پیامک به ``phone_number`` ارسال می‌کند.
        باید در کلاس فرزند پیاده‌سازی شود و True/False (موفقیت) برگرداند.
        """
        raise NotImplementedError(
            "زیرکلاس‌های BaseSMSBackend باید متد send_message را پیاده‌سازی کنند."
        )
