"""
تنظیمات مشترک بین محیط توسعه (dev) و پروداکشن (production).
هیچ‌وقت مستقیم استفاده نمی‌شود — همیشه از طریق dev.py یا production.py
ایمپورت می‌شود (`from .base import *`).
"""
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    "widget_tweaks",

    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",

    "accounts",
    "doctors",
    "patients",
    "payments",
    "appointments",
    "reviews",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "patients.context_processors.wallet_balance",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

AUTH_USER_MODEL = "accounts.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

SITE_ID = 1

# صفحه‌ی خطای CSRF هم هم‌شکل با بقیه‌ی صفحات خطا (400/403/404/500) باشد.
CSRF_FAILURE_VIEW = "config.views.csrf_failure_view"

# --- تنظیمات django-allauth (ورود با گوگل) ---
# مدل User ما اصلاً فیلدی به اسم username ندارد (نه فقط این‌که پر کردنش
# اختیاریه) — بدون این خط، allauth روی save_user سعی می‌کند برای کاربر
# یک username یکتا بسازد و چون چنین فیلدی روی مدل نیست با
# FieldDoesNotExist کرش می‌کند. ACCOUNT_USERNAME_REQUIRED=False به‌تنهایی
# این مشکل را حل نمی‌کند، چون فقط اجباری بودنش را در فرم لغو می‌کند.
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USER_MODEL_EMAIL_FIELD = "email"
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_AUTHENTICATION_METHOD = "email"
SOCIALACCOUNT_LOGIN_ON_GET = True  # مستقیم به صفحه ورود گوگل برو، بدون صفحه واسط
SOCIALACCOUNT_ADAPTER = "accounts.adapters.CustomSocialAccountAdapter"
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
        "APP": {
            "client_id": config("GOOGLE_CLIENT_ID", default=""),
            "secret": config("GOOGLE_CLIENT_SECRET", default=""),
            "key": "",
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "fa-ir"
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# توجه: نسخه‌ی «Manifest» (هش‌دار/cache-busting) فقط در production.py ست
# می‌شود، نه اینجا. آن نسخه هر بار به فایل staticfiles.json (خروجی
# collectstatic) نیاز دارد و اگر پیدا نشود، هر صفحه‌ای که از تگ
# {% static %} استفاده کند (که در base.html هست) با ValueError/500 کرش
# می‌کند. چون dev.py و test.py هیچ‌کدام collectstatic اجرا نمی‌کنند (و
# نباید هم اجرا کنند)، از نسخه‌ی ساده و بدون‌منیفست استفاده می‌کنیم که در
# هر حالتی (collectstatic اجرا شده باشد یا نه) کار می‌کند.
#
# از STORAGES (روش جدید و توصیه‌شده‌ی جنگو ۴٫۲+) استفاده می‌کنیم، نه
# STATICFILES_STORAGE قدیمی، که در جنگو ۵٫۱+ منسوخ شده است.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "accounts:redirect_after_login"
LOGOUT_REDIRECT_URL = "accounts:login"

CELERY_BROKER_URL = config("REDIS_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = config("REDIS_URL", default="redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"

OTP_EXPIRY_MINUTES = 5

# مقادیر SMS_API_KEY/SMS_SENDER_LINE مشترکند؛ خودِ SMS_BACKEND (که مشخص می‌کند
# کدام بک‌اند فعال است) در dev.py و production.py جدا تعریف می‌شود چون
# پیش‌فرضش بین دو محیط فرق دارد.
SMS_API_KEY = config("SMS_API_KEY", default="")
SMS_SENDER_LINE = config("SMS_SENDER_LINE", default="")
