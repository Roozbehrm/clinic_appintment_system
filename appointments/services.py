from django.core.exceptions import ValidationError
from django.db import transaction as db_transaction
from django.utils import timezone
from datetime import datetime
from django.core.mail import send_mail

from .models import Appointment

def book_appointment(patient, time_slot_id):
    from doctors.models import TimeSlot
    
    with db_transaction.atomic():
        try:
            slot = TimeSlot.objects.select_for_update().get(id=time_slot_id)
        except TimeSlot.DoesNotExist:
            raise ValidationError("بازه زمانی مورد نظر یافت نشد.")

        if slot.status != "free":
            raise ValidationError("این زمان قبلاً رزرو شده است.")
            
        fee = slot.doctor.consultation_fee
        
        # بررسی موجودی و کسر از کیف پول
        if patient.wallet.balance < fee:
            raise ValidationError("موجودی کیف پول کافی نیست.")
            
        patient.wallet.balance -= fee
        patient.wallet.save()

        appointment_obj = Appointment.objects.create(
            patient=patient,
            time_slot=slot,
            price=fee,
            status="confirmed"
        )

        slot.status = "booked"
        slot.save()

    # ارسال ایمیل تاییدیه (برای پاس شدن تست mailoutbox)
    try:
        send_mail(
            subject="تایید نوبت",
            message="نوبت شما با موفقیت رزرو شد.",
            from_email="noreply@medapp.local",
            recipient_list=[patient.profile.user.email],
            fail_silently=True,
        )
    except Exception:
        pass

    return appointment_obj


def cancel_appointment(appointment):
    if appointment.status not in ["pending", "confirmed"]:
        raise ValidationError("این نوبت قابل لغو نیست.")

    with db_transaction.atomic():
        appointment.status = "cancelled"
        appointment.save()

        slot = appointment.time_slot
        slot.status = "free"
        slot.save()

        # بازگشت وجه به کیف پول بیمار
        appointment.patient.wallet.balance += appointment.price
        appointment.patient.wallet.save()
        
    return appointment


def complete_appointment(appointment):
    if appointment.status != "confirmed":
        raise ValidationError("فقط نوبت‌های تایید شده قابل تکمیل هستند.")

    appointment.status = "completed"
    appointment.save()
    return appointment


def auto_complete_past_appointments(patient=None, doctor=None):
    queryset = Appointment.objects.filter(status="confirmed")

    if patient:
        queryset = queryset.filter(patient=patient)
    if doctor:
        queryset = queryset.filter(time_slot__doctor=doctor)

    completed_count = 0
    now = timezone.now()

    for appointment in queryset:
        slot = appointment.time_slot
        
        visit_end_datetime = timezone.make_aware(
            datetime.combine(slot.visit_date, slot.end_time)
        )

        if visit_end_datetime < now:
            appointment.status = "completed"
            appointment.save()
            completed_count += 1

    return completed_count