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


# def issue_otp(user, purpose):
#     OTP.objects.filter(user=user, purpose=purpose, is_used=False).update(is_used=True)
#     otp = OTP.objects.create(user=user, purpose=purpose)
#     _deliver_otp(user, otp)
#     return otp
import random
from sms.utils import send_sms 

def issue_otp(user, reason="login"):
    """
    تولید کد یکبار مصرف، ذخیره آن و ارسال پیامک به کاربر
    """
    # تولید یک کد ۶ رقمی رندوم
    otp_code = str(random.randint(100000, 999999))
    
    # TODO: اینجا باید کد تولید شده رو توی دیتابیس یا کش برای این کاربر ذخیره کنی
    # تا موقعی که ویوی VerifyOTPView فراخوانی میشه، بتونی چکش کنی.
    
    if reason == "signup":
        text = f"خوش آمدید!\nکد تایید ثبت‌نام شما:\n{otp_code}"
    elif reason == "password_reset":
        text = f"درخواست بازیابی رمز عبور\nکد تایید:\n{otp_code}"
    else:
        text = f"کد ورود شما\n{otp_code}"
        
    is_sent = send_sms(user.phone_number, text)
    
    return is_sent


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
