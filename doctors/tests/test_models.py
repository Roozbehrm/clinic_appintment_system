import pytest
from django.db import IntegrityError, transaction

from doctors.models import Doctor, TimeSlot, WorkingHour


@pytest.mark.django_db
class TestDoctor:
    def test_str_uses_full_name(self, doctor_user):
        assert str(doctor_user) == "دکتر تست"

    def test_average_rating_is_zero_with_no_reviews(self, doctor_user):
        assert doctor_user.average_rating == 0
        assert doctor_user.review_count == 0

    def test_average_rating_reflects_reviews(self, doctor_user, patient_user, free_time_slot):
        from appointments.models import Appointment
        from reviews.models import Review

        appointment = Appointment.objects.create(
            patient=patient_user, time_slot=free_time_slot,
            price=200000, status="completed",
        )
        Review.objects.create(appointment=appointment, rating=4)

        assert doctor_user.average_rating == 4.0
        assert doctor_user.review_count == 1

    def test_mcc_must_be_unique(self, doctor_user, specialty):
        from accounts.models import User, Profile

        other_user = User.objects.create(phone_number="09129999999", email="doc2@example.com")
        other_profile = Profile.objects.create(user=other_user, full_name="دکتر دو")

        # نکته: خطای مورد انتظار را داخل transaction.atomic() (savepoint) قرار
        # می‌دهیم، وگرنه روی برخی دیتابیس‌ها (مثل PostgreSQL) کل تراکنش تست
        # بعد از IntegrityError خراب می‌شود و دستورهای بعدی خطا می‌دهند.
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Doctor.objects.create(
                    profile=other_profile, specialty=specialty,
                    mcc=doctor_user.mcc,  # همان mcc دکتر قبلی — باید رد شود
                    consultation_fee=100000,
                )

        # اثبات این‌که تراکنش سالم مانده و ادامه‌ی تست بدون خطا کار می‌کند
        assert Doctor.objects.filter(mcc=doctor_user.mcc).count() == 1


@pytest.mark.django_db
class TestWorkingHour:
    def test_unique_together_prevents_exact_duplicate(self, doctor_user, working_hour):
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                WorkingHour.objects.create(
                    doctor=doctor_user,
                    day_of_week=working_hour.day_of_week,
                    start_time=working_hour.start_time,
                    end_time=working_hour.end_time,
                )

        assert WorkingHour.objects.filter(doctor=doctor_user).count() == 1


@pytest.mark.django_db
class TestTimeSlot:
    def test_is_free_property(self, free_time_slot):
        assert free_time_slot.is_free is True
        free_time_slot.status = "booked"
        assert free_time_slot.is_free is False

    def test_unique_together_prevents_same_doctor_date_start_time(self, doctor_user, free_time_slot):
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                TimeSlot.objects.create(
                    doctor=doctor_user,
                    visit_date=free_time_slot.visit_date,
                    start_time=free_time_slot.start_time,
                    end_time="10:00",
                )

        assert TimeSlot.objects.filter(doctor=doctor_user).count() == 1

