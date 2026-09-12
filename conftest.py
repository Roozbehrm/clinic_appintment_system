"""
فیکسچرهای مشترک بین تست‌های همه‌ی اپ‌ها.
هر فیکسچری که به دیتابیس نیاز دارد، وابستگی `db` (فیکسچر خودِ pytest-django)
را صریح می‌گیرد تا تراکنش‌های تست به‌درستی مدیریت شوند.
"""
import pytest

from accounts.models import User, Profile
from doctors.models import Specialty, Doctor, WorkingHour, TimeSlot
from patients.models import Patient
from payments.models import Wallet

TEST_PASSWORD = "StrongPass123!"


@pytest.fixture(autouse=True)
def clear_sms_outbox():
    """
    outbox پیامک (sms.backends.locmem) یک لیست سطح-ماژول است و برخلاف
    mail.outbox جنگو، به‌صورت خودکار بین تست‌ها پاک نمی‌شود. اگر این فیکسچر
    نبود، تست بعدی می‌توانست پیامک‌های تست قبلی را هم ببیند و نتیجه‌ی
    غلط بدهد. autouse=True یعنی نیازی نیست هر تست صریح درخواستش کند.
    """
    from sms.backends import locmem
    locmem.outbox.clear()
    yield
    locmem.outbox.clear()


@pytest.fixture
def specialty(db):
    return Specialty.objects.create(name="قلب و عروق")


@pytest.fixture
def doctor_user(db, specialty):
    """یک کاربر پزشکِ کامل (User + Profile + Doctor)، تایید‌شده و با رمز عبور مشخص."""
    user = User.objects.create(
        phone_number="09120000001",
        email="doctor@example.com",
        is_verified=True,
    )
    user.set_password(TEST_PASSWORD)
    user.save()

    profile = Profile.objects.create(user=user, full_name="دکتر تست")
    doctor = Doctor.objects.create(
        profile=profile,
        specialty=specialty,
        mcc="123456",
        consultation_fee=200000,
        is_active=True,
    )
    return doctor


@pytest.fixture
def patient_user(db):
    """یک کاربر بیمارِ کامل (User + Profile + Patient + Wallet)، تایید‌شده."""
    user = User.objects.create(
        phone_number="09120000002",
        email="patient@example.com",
        is_verified=True,
    )
    user.set_password(TEST_PASSWORD)
    user.save()

    profile = Profile.objects.create(user=user, full_name="بیمار تست")
    patient = Patient.objects.create(profile=profile)
    Wallet.objects.create(patient=patient, balance=1000000)
    return patient


@pytest.fixture
def working_hour(db, doctor_user):
    """یک بازه‌ی کاری برای doctor_user در روز شنبه (day_of_week=0)، ۸ تا ۱۲."""
    from datetime import time

    return WorkingHour.objects.create(
        doctor=doctor_user,
        day_of_week=0,
        start_time=time(8, 0),
        end_time=time(12, 0),
        slot_duration_minutes=30,
    )


@pytest.fixture
def free_time_slot(db, doctor_user):
    """یک اسلات خالیِ دستی برای doctor_user، مستقل از generate_time_slots."""
    from datetime import date, time, timedelta
    return TimeSlot.objects.create(
        doctor=doctor_user,
        visit_date=date.today() + timedelta(days=1),
        start_time=time(9, 0),
        end_time=time(9, 30),
        status="free",
    )
