import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from sms.utils import send_sms

logger = logging.getLogger(__name__)


@shared_task
def send_sms_task(phone_number, message):
    try:
        send_sms(phone_number, message)
    except Exception:
        logger.exception("ارسال پیامک به %s ناموفق بود", phone_number)


@shared_task
def send_email_task(subject, message, recipient_list, fail_silently=False):
    try:
        send_mail(
            subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list,
            fail_silently=fail_silently,
        )
    except Exception:
        logger.exception("ارسال ایمیل به %s ناموفق بود", recipient_list)
