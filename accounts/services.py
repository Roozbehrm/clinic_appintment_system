import logging

from django.db.models import Q
from django.utils import timezone

from .models import OTP, User
from .tasks import send_email_task, send_sms_task

logger = logging.getLogger(__name__)


def find_user_by_identifier(identifier):
    """کاربر را بر اساس شماره تلفن یا ایمیل (هرکدام که وارد شده) پیدا می‌کند."""
    identifier = (identifier or "").strip()
    if not identifier:
        return None
    if "@" in identifier:
        return User.objects.filter(email__iexact=identifier).first()
    return User.objects.filter(phone_number=identifier).first()


def issue_otp(user, purpose, channel="both"):
    OTP.objects.filter(user=user, purpose=purpose, is_used=False).update(is_used=True)
    OTP.objects.filter(user=user).filter(
        Q(is_used=True) | Q(expires_at__lt=timezone.now())
    ).delete()
    otp = OTP.objects.create(user=user, purpose=purpose)
    _deliver_otp(user, otp, channel=channel)
    return otp


def _deliver_otp(user, otp, channel="both"):
    message = f"کد تایید شما: {otp.code}"

    if channel == "email":

        _send_otp_email(user, message)
        return

    if channel == "sms":

        _send_sms_safe(user, message)
        return

    _send_sms_safe(user, message)
    _send_otp_email(user, message)


def _send_sms_safe(user, message):
    if not user.phone_number:

        return
    try:
        send_sms_task.delay(user.phone_number, message)
    except Exception:

        logger.exception("صف‌کردن ارسال پیامک برای %s ناموفق بود", user.phone_number)


def _send_otp_email(user, message):
    if not user.email:
        return
    try:
        send_email_task.delay("کد تایید نوبت‌دهی پزشکان", message, [user.email])
    except Exception:
        logger.exception("صف‌کردن ارسال ایمیل OTP برای %s ناموفق بود", user.email)


def send_new_account_credentials(user, password):
 
    message = (
        "حساب پزشک شما در سامانه‌ی نوبت‌دهی ساخته شد.\n"
        f"شماره‌ی ورود: {user.phone_number}\n"
        f"رمز عبور: {password}\n"
        "پیشنهاد می‌شود پس از اولین ورود، رمز عبور را از پروفایل تغییر دهید."
    )
    _send_sms_safe(user, message)
    if user.email:
        try:
            send_email_task.delay("اطلاعات ورود حساب پزشک", message, [user.email])
        except Exception:
            logger.exception("صف‌کردن ارسال ایمیل اطلاعات ورود پزشک برای %s ناموفق بود", user.email)


def send_appointment_confirmation_email(appointment):
    patient_email = appointment.patient.profile.user.email
    if not patient_email:
        return
    try:
        send_email_task.delay(
            "تاییدیه رزرو نوبت",
            f"نوبت شما با دکتر {appointment.time_slot.doctor.profile.full_name} "
            f"در تاریخ {appointment.time_slot.visit_date} ساعت {appointment.time_slot.start_time} "
            f"با موفقیت رزرو شد.",
            [patient_email],
        )
    except Exception:
        logger.exception("صف‌کردن ارسال ایمیل تاییدیه‌ی نوبت برای %s ناموفق بود", patient_email)
