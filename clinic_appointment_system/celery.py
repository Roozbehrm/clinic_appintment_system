import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_appointment_system.settings')

app = Celery('clinic_appointment_system')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()