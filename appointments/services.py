from django.core.exceptions import ValidationError
from django.db import transaction as db_transaction

from doctors.models import TimeSlot
from payments.services import pay_for_appointment
from accounts.services import send_appointment_confirmation_email

from .models import Appointment


def book_appointment(patient, time_slot_id):
    with db_transaction.atomic():
        slot = TimeSlot.objects.select_for_update().get(pk=time_slot_id)
        if slot.status != "free":
            raise ValidationError("این نوبت دیگر خالی نیست.")

        doctor = slot.doctor
        price = doctor.consultation_fee

        appointment = Appointment.objects.create(
            patient=patient, time_slot=slot, price=price, status="pending",
        )

        wallet = patient.wallet
        pay_for_appointment(wallet, appointment, price)

        appointment.status = "confirmed"
        appointment.save()

        slot.status = "booked"
        slot.save()

    send_appointment_confirmation_email(appointment)
    return appointment


def cancel_appointment(appointment):
    from payments.services import refund_appointment
    with db_transaction.atomic():
        if appointment.status not in ("pending", "confirmed"):
            raise ValidationError("این نوبت قابل لغو نیست.")
        appointment.status = "cancelled"
        appointment.save()

        slot = appointment.time_slot
        slot.status = "free"
        slot.save()

        refund_appointment(appointment.patient.wallet, appointment, appointment.price)
    return appointment


def complete_appointment(appointment):
    if appointment.status != "confirmed":
        raise ValidationError("فقط نوبت تاییدشده قابل تکمیل است.")
    appointment.status = "completed"
    appointment.save()
    return appointment


def auto_complete_past_appointments(patient=None, doctor=None):
    """
    نوبت‌های تاییدشده‌ای که زمان ویزیت آن‌ها گذشته را به‌صورت خودکار
    'انجام‌شده' علامت می‌زند تا امکان ثبت نظر برای بیمار فراهم شود.
    """
    from django.utils import timezone
    from datetime import datetime

    now = timezone.now()

    qs = Appointment.objects.filter(status="confirmed")
    if patient is not None:
        qs = qs.filter(patient=patient)
    if doctor is not None:
        qs = qs.filter(time_slot__doctor=doctor)

    for appointment in qs.select_related("time_slot"):
        slot = appointment.time_slot
        naive_end = datetime.combine(slot.visit_date, slot.end_time)
        visit_end = timezone.make_aware(naive_end) if timezone.is_naive(naive_end) else naive_end
        if visit_end < now:
            appointment.status = "completed"
            appointment.save()