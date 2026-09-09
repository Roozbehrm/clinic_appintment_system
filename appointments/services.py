from django.core.exceptions import ValidationError
from django.db import transaction as db_transaction
from django.utils import timezone
from datetime import datetime

# کامنت شده تا زمان تکمیل تسک‌های بقیه
# from doctors.models import TimeSlot
# from payments.services import pay_for_appointment, refund_appointment
# from accounts.services import send_appointment_confirmation_email
from .models import Appointment

# TASK T3.5 (Mahyar)
def book_appointment(patient, time_slot_id):
    # برای جلوگیری از ارور circular import
    from doctors.models import TimeSlot
    
    # متغیری برای نگهداری آبجکت نوبت در سطح تابع
    appointment_obj = None

    with db_transaction.atomic():
    #جلوگیری از رزرو همزمان یک نوبت
        try:
            slot = TimeSlot.objects.select_for_update().get(id=time_slot_id)
        except TimeSlot.DoesNotExist:
            raise ValidationError("بازه زمانی مورد نظر یافت نشد.")

        # بررسی وضعیت 
        if slot.status != "free":
            raise ValidationError("این زمان قبلاً رزرو شده است.")

        appointment_obj = Appointment.objects.create(
            patient=patient,
            time_slot=slot,
            price=slot.doctor.consultation_fee,
            status="pending"
        )

        #(موقت)
        try:
            # TODO: Uncomment after T4.3
            # pay_for_appointment(patient.wallet, appointment_obj, appointment_obj.price)
            pass
        except Exception as e:
            raise ValidationError(f"خطا در پرداخت: {str(e)}")

        # تایید نوبت و تغییر وضعیت اسلات
        appointment_obj.status = "confirmed"
        appointment_obj.save()

        slot.status = "booked"
        slot.save()

    # ارسال ایمیل تاییدیه خارج از بلاک تراکنش
    try:
        # TODO: Uncomment when ready
        # send_appointment_confirmation_email(appointment_obj)
        pass
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

        # (موقت)
        # TODO: Uncomment after T4.3
        # from payments.services import refund_appointment
        # refund_appointment(appointment.patient.wallet, appointment.price)
        
    return appointment


def complete_appointment(appointment):
    if appointment.status != "confirmed":
        raise ValidationError("فقط نوبت‌های تایید شده قابل تکمیل هستند.")

    appointment.status = "completed"
    appointment.save()
    return appointment


def auto_complete_past_appointments(patient=None, doctor=None):
    # گرفتن نوبت‌های تایید شده
    queryset = Appointment.objects.filter(status="confirmed")

# فیلترهای اختیاری
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