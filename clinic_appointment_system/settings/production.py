"""
تنظیمات محیط پروداکشن.
فعال‌سازی: DJANGO_SETTINGS_MODULE=config.settings.production
(در docker-compose.yml از قبل همین‌طور تنظیم شده).

نکته‌ی امنیتی: SECRET_KEY و ALLOWED_HOSTS اینجا عمداً «مقدار پیش‌فرض» ندارند —
اگر در .env تنظیم نشده باشند، اجرای برنامه با خطا متوقف می‌شود؛ بهتر از این
است که پروداکشن به‌صورت خاموش/ناامن با مقادیر توسعه بالا بیاید.
"""
from decouple import config, Csv

from .base import *  # noqa: F401,F403

SECRET_KEY = config("SECRET_KEY")  # بدون default — باید در .env ست شود
DEBUG = False
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())  # بدون default

# فقط در پروداکشن نسخه‌ی هش‌دار (Manifest) استاتیک فایل‌ها را روشن می‌کنیم؛
# چون docker-compose.yml قبل از اجرای gunicorn حتماً collectstatic را
# اجرا می‌کند (پس فایل manifest همیشه از قبل آماده است)، اینجا امن است.
STORAGES = {
    **STORAGES,
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", default="db"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

# ایمیل واقعی (SMTP) به‌جای کنسول
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER or "noreply@medapp.local"

# پیامک واقعی (پیش‌فرض Kavenegar) به‌جای کنسول — اگر SMS_API_KEY ست نشده
# باشد، اولین تلاش برای ارسال OTP خطا می‌دهد؛ این عمدی است تا فراموش نشود.
SMS_BACKEND = config("SMS_BACKEND", default="sms.backends.kavenegar.KavenegarBackend")

# --------------------------------------------------------------------- #
# سخت‌سازی امنیتی مخصوص پروداکشن
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="", cast=Csv())
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=60 * 60 * 24 * 30, cast=int)  # ۳۰ روز
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
# اگر پشت یک ریورس‌پروکسی/لودبالانسر (nginx, Render, Railway و ...) هستید
# که خودش SSL ترمینیت می‌کند، این هدر لازم است تا جنگو درخواست را HTTPS بداند.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# --------------------------------------------------------------------- #
# لاگ‌گیری — خطاهای سطح ERROR به‌جای گم‌شدن، در کنسول/لاگ کانتینر چاپ می‌شوند
# (که با docker logs یا هر سرویس لاگ‌آوری قابل مشاهده‌اند).
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
