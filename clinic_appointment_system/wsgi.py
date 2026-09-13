import os

from decouple import config
from django.core.wsgi import get_wsgi_application

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", config("DJANGO_SETTINGS_MODULE", default="clinic_appointment_system.settings.dev")
)
application = get_wsgi_application()
