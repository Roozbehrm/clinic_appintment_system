from datetime import date, time, timedelta
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

INITIAL_WALLET_BALANCE = Decimal("1000000")


@pytest.mark.django_db
class TestAppointmentBooking:
    def test_successful_booking_confirms_appointment_and_charges_wallet(
        self, mailoutbox, patient_user, doctor_user, free_time_slot
    ):
        appointment = book_appointment(patient_user, free_time_slot.id)

        assert appointment.status == "confirmed"
        assert appointment.price == doctor_user.consultation_fee

        free_time_slot.refresh_from_db()
        assert free_time_slot.status == "booked"

        patient_user.wallet.refresh_from_db()
        assert patient_user.wallet.balance == INITIAL_WALLET_BALANCE - doctor_user.consultation_fee

        assert len(mailoutbox) == 1

    def test_cannot_book_a_slot_that_is_no_longer_free(self, patient_user, free_time_slot):
        free_time_slot.status = "booked"
        free_time_slot.save()

        with pytest.raises(ValidationError):
            book_appointment(patient_user, free_time_slot.id)

    def test_booking_fails_cleanly_when_wallet_balance_is_insufficient(
        self, patient_user, doctor_user, free_time_slot
    ):
        doctor_user.consultation_fee = 5_000_000  # بیشتر از موجودی کیف‌پول (۱۰۰۰۰۰۰)
        doctor_user.save()

        with pytest.raises(ValidationError):
            book_appointment(patient_user, free_time_slot.id)

        assert not Appointment.objects.filter(patient=patient_user).exists()
        free_time_slot.refresh_from_db()
        assert free_time_slot.status == "free"
        patient_user.wallet.refresh_from_db()
        assert patient_user.wallet.balance == INITIAL_WALLET_BALANCE


@pytest.mark.django_db
class TestAppointmentCancellation:
    def test_cancelling_confirmed_appointment_refunds_wallet_and_frees_slot(
        self, patient_user, doctor_user, free_time_slot
    ):
        free_time_slot.status = "booked"
        free_time_slot.save()
        patient_user.wallet.balance = Decimal("800000")
        patient_user.wallet.save()

        appointment = Appointment.objects.create(
            patient=patient_user, time_slot=free_time_slot, price=200000, status="confirmed",
        )
        cancel_appointment(appointment)

        appointment.refresh_from_db()
        free_time_slot.refresh_from_db()
        patient_user.wallet.refresh_from_db()

        assert appointment.status == "cancelled"
        assert free_time_slot.status == "free"
        assert patient_user.wallet.balance == INITIAL_WALLET_BALANCE

    def test_cancelling_pending_appointment_is_also_allowed(self, patient_user, free_time_slot):
        appointment = Appointment.objects.create(
            patient=patient_user, time_slot=free_time_slot, price=150000, status="pending",
        )
        cancel_appointment(appointment)

        appointment.refresh_from_db()
        assert appointment.status == "cancelled"

    def test_cannot_cancel_an_already_completed_appointment(self, patient_user, free_time_slot):
        appointment = Appointment.objects.create(
            patient=patient_user, time_slot=free_time_slot, price=200000, status="completed",
        )
        with pytest.raises(ValidationError):
            cancel_appointment(appointment)


@pytest.mark.django_db
class TestAppointmentCompletion:
    def test_confirmed_appointment_becomes_completed(self, patient_user, free_time_slot):
        appointment = Appointment.objects.create(
            patient=patient_user, time_slot=free_time_slot, price=200000, status="confirmed",
        )
        complete_appointment(appointment)

        appointment.refresh_from_db()
        assert appointment.status == "completed"

    def test_non_confirmed_appointment_cannot_be_completed(self, patient_user, free_time_slot):
        appointment = Appointment.objects.create(
            patient=patient_user, time_slot=free_time_slot, price=200000, status="pending",
        )
        with pytest.raises(ValidationError):
            complete_appointment(appointment)


@pytest.mark.django_db
class TestAutoCompletePastAppointments:
    def test_only_past_confirmed_appointments_get_completed(self, patient_user, doctor_user):
        past_slot = TimeSlot.objects.create(
            doctor=doctor_user, visit_date=date.today() - timedelta(days=1),
            start_time=time(9, 0), end_time=time(9, 30), status="booked",
        )
        future_slot = TimeSlot.objects.create(
            doctor=doctor_user, visit_date=date.today() + timedelta(days=1),
            start_time=time(9, 0), end_time=time(9, 30), status="booked",
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

    def test_non_confirmed_past_appointments_are_left_untouched(self, patient_user, doctor_user):
        past_slot = TimeSlot.objects.create(
            doctor=doctor_user, visit_date=date.today() - timedelta(days=2),
            start_time=time(9, 0), end_time=time(9, 30), status="free",
        )
        appointment = Appointment.objects.create(
            patient=patient_user, time_slot=past_slot, price=100000, status="cancelled",
        )

        auto_complete_past_appointments(patient=patient_user)

        appointment.refresh_from_db()
        assert appointment.status == "cancelled"