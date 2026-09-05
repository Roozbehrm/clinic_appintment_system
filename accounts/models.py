import random
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(verbose_name="شماره تلفن", max_length=15, unique=True)
    email = models.EmailField(verbose_name="ایمیل", unique=True)
    is_verified = models.BooleanField(verbose_name="تایید شده", default=False)
    is_staff = models.BooleanField(verbose_name="کارمند", default=False)
    is_active = models.BooleanField(verbose_name="فعال", default=True)
    date_joined = models.DateTimeField(verbose_name="تاریخ عضویت", auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"

    def __str__(self):
        return self.phone_number

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
        return f"{self.user.phone_number} - {self.code}"


class Profile(models.Model):
    GENDER_CHOICES = [("male", "مرد"), ("female", "زن")]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(verbose_name="نام و نام خانوادگی", max_length=150, blank=True)
    avatar = models.ImageField(verbose_name="آواتار", upload_to="avatars/", blank=True, null=True)
    national_code = models.CharField(verbose_name="کد ملی", max_length=10, blank=True)
    gender = models.CharField(verbose_name="جنسیت", max_length=10, choices=GENDER_CHOICES, blank=True)
    address = models.CharField(verbose_name="آدرس", max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "پروفایل"
        verbose_name_plural = "پروفایل‌ها"

    def __str__(self):
        return self.full_name or self.user.phone_number
