from datetime import timedelta

import pytest
from django.utils import timezone

from accounts.models import OTP, Profile, User


@pytest.mark.django_db
class TestUserRoles:
    def test_user_without_profile_is_neither_doctor_nor_patient(self):
        user = User.objects.create(phone_number="09121111111", email="a@example.com")
        assert user.is_doctor is False
        assert user.is_patient is False

    def test_user_is_doctor(self, doctor_user):
        user = doctor_user.profile.user
        assert user.is_doctor is True
        assert user.is_patient is False

    def test_user_is_patient(self, patient_user):
        user = patient_user.profile.user
        assert user.is_patient is True
        assert user.is_doctor is False


@pytest.mark.django_db
class TestOTP:
    def test_save_autogenerates_code_and_expiry(self):
        user = User.objects.create(phone_number="09122222222", email="b@example.com")
        otp = OTP.objects.create(user=user, purpose="register")

        assert otp.code is not None
        assert len(otp.code) == 6
        assert otp.expires_at > timezone.now()

    def test_is_valid_true_for_fresh_unused_code(self):
        user = User.objects.create(phone_number="09123333333", email="c@example.com")
        otp = OTP.objects.create(user=user, purpose="login")
        assert otp.is_valid() is True

    def test_is_valid_false_when_used(self):
        user = User.objects.create(phone_number="09124444444", email="d@example.com")
        otp = OTP.objects.create(user=user, purpose="login", is_used=True)
        assert otp.is_valid() is False

    def test_is_valid_false_when_expired(self):
        user = User.objects.create(phone_number="09125555555", email="e@example.com")
        otp = OTP.objects.create(
            user=user, purpose="login",
            expires_at=timezone.now() - timedelta(minutes=1),
        )
        assert otp.is_valid() is False


@pytest.mark.django_db
class TestProfile:
    def test_str_uses_full_name_when_set(self):
        user = User.objects.create(phone_number="09126666666", email="f@example.com")
        profile = Profile.objects.create(user=user, full_name="علی رضایی")
        assert str(profile) == "علی رضایی"

    def test_str_falls_back_to_phone_number_when_no_name(self):
        user = User.objects.create(phone_number="09127777777", email="g@example.com")
        profile = Profile.objects.create(user=user, full_name="")
        assert str(profile) == "09127777777"
