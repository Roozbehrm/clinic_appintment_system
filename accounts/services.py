import logging
from django.core.mail import send_mail
from django.conf import settings
from sms.utils import send_sms
from .models import OTP, User
logger = logging.getLogger(__name__)


def find_user_by_identifier(identifier):
    identifier = (identifier or "").strip()
    if not identifier:
        return None
    if "@" in identifier:
        return User.objects.filter(email__iexact=identifier).first()
    return User.objects.filter(phone_number=identifier).first()


def issue_otp(user, purpose, channel="both"):
    OTP.objects.filter(user=user, purpose=purpose, is_used=False).update(is_used=True)
    otp = OTP.objects.create(user=user, purpose=purpose)
    _deliver_otp(user, otp, channel=channel)
    return otp


def _deliver_otp(user, otp, channel="both"):
    message = f"کد تایید شما: {otp.code}"

    if channel == "email":
        _send_otp_email(user, message)
        return


    _send_sms_safe(user, message)
    _send_otp_email(user, message)


def _send_sms_safe(user, message):
    if not user.phone_number:
        return
    try:
        send_sms(user.phone_number, message)
    except Exception:
        logger.exception("ارسال پیامک OTP به %s ناموفق بود", user.phone_number)


def _send_otp_email(user, message):
    if not user.email:
        return
    try:
        send_mail(
            "کد تایید نوبت‌دهی پزشکان",
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
    except Exception:
        logger.exception("ارسال ایمیل OTP به %s ناموفق بود", user.email)


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
            send_mail(
                "اطلاعات ورود حساب پزشک",
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception:
            logger.exception("ارسال ایمیل اطلاعات ورود پزشک به %s ناموفق بود", user.email)


def send_appointment_confirmation_email(appointment):
    patient_email = appointment.patient.profile.user.email
    if not patient_email:
        return
    try:
        send_mail(
            "تاییدیه رزرو نوبت",
            f"نوبت شما با دکتر {appointment.time_slot.doctor.profile.full_name} "
            f"در تاریخ {appointment.time_slot.visit_date} ساعت {appointment.time_slot.start_time} "
            f"با موفقیت رزرو شد.",
            settings.DEFAULT_FROM_EMAIL,
            [patient_email],
            fail_silently=False,
        )
    except Exception:
        logger.exception("ارسال ایمیل تاییدیه‌ی نوبت به %s ناموفق بود", patient_email)
