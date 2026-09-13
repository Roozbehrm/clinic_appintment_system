import random
from datetime import timedelta
from io import BytesIO

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from PIL import Image, ImageOps

from .managers import UserManager

# حداکثر ابعاد آواتار بعد از فشرده‌سازی (پیکسل) و کیفیت JPEG خروجی.
AVATAR_MAX_DIMENSION = 600
AVATAR_JPEG_QUALITY = 82


class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(
        "شماره تلفن", max_length=15, unique=True, null=True, blank=True,
        help_text="برای کاربرانی که فقط با گوگل وارد شده‌اند خالی می‌ماند.",
    )
    email = models.EmailField("ایمیل", unique=True)
    is_verified = models.BooleanField("تایید شده", default=False)
    is_staff = models.BooleanField("کارمند", default=False)
    is_active = models.BooleanField("فعال", default=True)
    date_joined = models.DateTimeField("تاریخ عضویت", auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"

    def __str__(self):
        return self.email

    @property
    def is_doctor(self):
        return hasattr(self, "profile") and hasattr(self.profile, "doctor")

    @property
    def is_patient(self):
        return hasattr(self, "profile") and hasattr(self.profile, "patient")


class OTP(models.Model):
    PURPOSE_CHOICES = [
        ("register", "ثبت‌نام"),
        ("login", "ورود"),
        ("otp_login", "ورود با کد یکبار مصرف"),
        ("reset_password", "بازیابی رمز عبور"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otps")
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = "کد یکبار مصرف"
        verbose_name_plural = "کدهای یکبار مصرف"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f"{random.randint(0, 999999):06d}"
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
        super().save(*args, **kwargs)

    def is_valid(self):
        return (not self.is_used) and timezone.now() <= self.expires_at

    def __str__(self):
        return f"{self.user.email} - {self.code}"


class Profile(models.Model):
    GENDER_CHOICES = [("male", "مرد"), ("female", "زن")]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField("نام و نام خانوادگی", max_length=150, blank=True)
    avatar = models.ImageField("آواتار", upload_to="avatars/", blank=True, null=True)
    avatar_pos_x = models.PositiveSmallIntegerField("موقعیت افقی آواتار (٪)", default=50)
    avatar_pos_y = models.PositiveSmallIntegerField("موقعیت عمودی آواتار (٪)", default=50)
    national_code = models.CharField("کد ملی", max_length=10, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    address = models.CharField("آدرس", max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "پروفایل"
        verbose_name_plural = "پروفایل‌ها"

    def __str__(self):
        return self.full_name or self.user.phone_number or self.user.email

    def save(self, *args, **kwargs):
  
        if self.avatar and not self.avatar._committed:
            self.avatar = self._compress_avatar(self.avatar)
        super().save(*args, **kwargs)

    def _compress_avatar(self, avatar_field):
        image = Image.open(avatar_field)
        image = ImageOps.exif_transpose(image)  
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")

        image.thumbnail((AVATAR_MAX_DIMENSION, AVATAR_MAX_DIMENSION), Image.LANCZOS)

        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=AVATAR_JPEG_QUALITY, optimize=True)
        buffer.seek(0)

        name = avatar_field.name.rsplit(".", 1)[0] + ".jpg"
        new_file = ContentFile(buffer.read(), name=name)
        new_file._avatar_compressed = True
        return new_file
