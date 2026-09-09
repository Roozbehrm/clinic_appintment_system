from django.core.mail import send_mail
from django.conf import settings

from .models import OTP, User

# find user by phone number or email
def find_user_by_identifier(identifier):
    identifier = (identifier or "").strip()
    if not identifier:
        return None
    if "@" in identifier:
        return User.objects.filter(email__iexact=identifier).first()
    return User.objects.filter(phone_number=identifier).first()


def issue_otp(user, purpose):
    OTP.objects.filter(user=user, purpose=purpose, is_used=False).update(is_used=True)
    otp = OTP.objects.create(user=user, purpose=purpose)
    _deliver_otp(user, otp)
    return otp


def _deliver_otp(user, otp):
    print(f"[OTP] برای {user.phone_number}: {otp.code}")
    if user.email:
        try:
            send_mail(
                "کد تایید نوبت‌دهی پزشکان",
                f"کد تایید شما: {otp.code}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
        except Exception:
            pass
