"""
تنظیمات محیط توسعه‌ی لوکال.
فعال‌سازی: DJANGO_SETTINGS_MODULE=config.settings.dev (پیش‌فرض manage.py/wsgi.py).
"""
from decouple import config

from .base import *  # noqa: F401,F403

SECRET_KEY = config("SECRET_KEY", default="dev-insecure-secret-key")
DEBUG = True
ALLOWED_HOSTS = ["*"]

# پیش‌فرض SQLite برای صفر تا صد راه‌اندازی بدون نصب Postgres؛
# با USE_SQLITE=False در .env می‌توان به Postgres محلی هم وصل شد.
if config("USE_SQLITE", default=True, cast=bool):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("DB_NAME", default="medapp"),
            "USER": config("DB_USER", default="medapp"),
            "PASSWORD": config("DB_PASSWORD", default="medapp"),
            "HOST": config("DB_HOST", default="localhost"),
            "PORT": config("DB_PORT", default="5432"),
        }
    }

# در توسعه پیامک/ایمیل واقعی ارسال نمی‌شود؛ در کنسول چاپ می‌شود.
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
DEFAULT_FROM_EMAIL = config("EMAIL_HOST_USER", default="noreply@medapp.local")

SMS_BACKEND = config("SMS_BACKEND", default="sms.backends.console.ConsoleBackend")

# در توسعه نیازی به CSRF/Cookie امن (HTTPS) نیست.
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
