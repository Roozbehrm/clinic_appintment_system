from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from appointments.models import Appointment
from appointments.services import (
    auto_complete_past_appointments,
    book_appointment,
    cancel_appointment,
    complete_appointment,
)
from doctors.models import TimeSlot


@pytest.mark.django_db
class TestBookAppointment:
    def test_successful_booking_creates_confirmed_appointment(
        self, mailoutbox, patient_user, doctor_user, free_time_slot
    ):
        appointment = book_appointment(patient_user, free_time_slot.id)

        assert appointment.status == "confirmed"
        assert appointment.price == doctor_user.consultation_fee

        free_time_slot.refresh_from_db()
        assert free_time_slot.status == "booked"

        patient_user.wallet.refresh_from_db()
        assert patient_user.wallet.balance == Decimal("1000000") - doctor_user.consultation_fee

        assert len(mailoutbox) == 1  # ایمیل تاییدیه

    def test_raises_when_slot_not_free(self, patient_user, free_time_slot):
        free_time_slot.status = "booked"
        free_time_slot.save()

        with pytest.raises(ValidationError):
            book_appointment(patient_user, free_time_slot.id)

    def test_insufficient_balance_rolls_back_everything(
        self, patient_user, doctor_user, free_time_slot
    ):
        doctor_user.consultation_fee = 5000000  # بیشتر از موجودی کیف پول (۱۰۰۰۰۰۰)
        doctor_user.save()

        with pytest.raises(ValidationError):
            book_appointment(patient_user, free_time_slot.id)

        # به‌خاطر atomic بودن، هیچ‌کدام نباید باقی مانده باشد
        assert not Appointment.objects.filter(patient=patient_user).exists()
        free_time_slot.refresh_from_db()
        assert free_time_slot.status == "free"
        patient_user.wallet.refresh_from_db()
        assert patient_user.wallet.balance == Decimal("1000000")


@pytest.mark.django_db
class TestCancelAppointment:
    def test_cancel_confirmed_appointment_refunds_and_frees_slot(
        self, patient_user, doctor_user, free_time_slot
    ):
        free_time_slot.status = "booked"
        free_time_slot.save()
        appointment = Appointment.objects.create(
            patient=patient_user, time_slot=free_time_slot,
            price=200000, status="confirmed",
        )
        # فرض می‌کنیم موجودی از قبل بابت این نوبت کم شده بود
        patient_user.wallet.balance = Decimal("800000")
        patient_user.wallet.save()

        cancel_appointment(appointment)

        appointment.refresh_from_db()
        assert appointment.status == "cancelled"
        free_time_slot.refresh_from_db()
        assert free_time_slot.status == "free"
        patient_user.wallet.refresh_from_db()
        assert patient_user.wallet.balance == Decimal("1000000")

    def test_cannot_cancel_already_completed_appointment(
        self, patient_user, free_time_slot
    ):
        appointment = Appointment.objects.create(
            patient=patient_user, time_slot=free_time_slot,
            price=200000, status="completed",
        )
        with pytest.raises(ValidationError):
            cancel_appointment(appointment)


@pytest.mark.django_db
class TestCompleteAppointment:
    def test_confirmed_becomes_completed(self, patient_user, free_time_slot):
        appointment = Appointment.objects.create(
            patient=patient_user, time_slot=free_time_slot,
            price=200000, status="confirmed",
        )
        complete_appointment(appointment)
        appointment.refresh_from_db()
        assert appointment.status == "completed"

    def test_non_confirmed_raises(self, patient_user, free_time_slot):
        appointment = Appointment.objects.create(
            patient=patient_user, time_slot=free_time_slot,
            price=200000, status="pending",
        )
        with pytest.raises(ValidationError):
            complete_appointment(appointment)


@pytest.mark.django_db
class TestAutoCompletePastAppointments:
    def test_only_past_confirmed_appointments_are_completed(self, patient_user, doctor_user):
        past_slot = TimeSlot.objects.create(
            doctor=doctor_user, visit_date=date.today() - timedelta(days=1),
            start_time="09:00", end_time="09:30", status="booked",
        )
        future_slot = TimeSlot.objects.create(
            doctor=doctor_user, visit_date=date.today() + timedelta(days=1),
            start_time="09:00", end_time="09:30", status="booked",
        )
        past_appointment = Appointment.objects.create(
            patient=patient_user, time_slot=past_slot, price=100000, status="confirmed",
        )
        future_appointment = Appointment.objects.create(
            patient=patient_user, time_slot=future_slot, price=100000, status="confirmed",
        )

        auto_complete_past_appointments(patient=patient_user)

        past_appointment.refresh_from_db()
        future_appointment.refresh_from_db()
        assert past_appointment.status == "completed"
        assert future_appointment.status == "confirmed"

    def test_cancelled_appointments_are_untouched(self, patient_user, doctor_user):
        past_slot = TimeSlot.objects.create(
            doctor=doctor_user, visit_date=date.today() - timedelta(days=1),
            start_time="09:00", end_time="09:30", status="free",
        )
        appointment = Appointment.objects.create(
            patient=patient_user, time_slot=past_slot, price=100000, status="cancelled",
        )
        auto_complete_past_appointments(patient=patient_user)
        appointment.refresh_from_db()
        assert appointment.status == "cancelled"
