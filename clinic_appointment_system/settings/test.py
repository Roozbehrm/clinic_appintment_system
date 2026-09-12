
from .base import *  # noqa: F401,F403

SECRET_KEY = "test-secret-key-not-for-production"
DEBUG = False
ALLOWED_HOSTS = ["*"]

# for testing, we use an in-memory SQLite database to avoid creating a physical file.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Password hashing is slow by default; for tests, we use a fast hasher to speed up test execution.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
# outbox checking is done in tests, so we use the locmem backend for emails and SMS to capture them in memory.
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
DEFAULT_FROM_EMAIL = "test@medapp.local"
SMS_BACKEND = "sms.backends.locmem.LocmemBackend"

# media files are stored in a temporary directory during tests to avoid cluttering the project directory and to ensure isolation between test runs.
import tempfile  # noqa: E402
MEDIA_ROOT = tempfile.mkdtemp(prefix="medapp_test_media_")

# Celery tasks are executed synchronously during tests to simplify testing and avoid the need for a running Celery worker or broker.
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
