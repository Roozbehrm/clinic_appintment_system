from django.views.generic import FormView, UpdateView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Appointment
from .forms import AppointmentConfirmForm
from doctors.models import TimeSlot
from patients.models import Patient


# TASK T3.3 (Mahyar) 
class AppointmentCreateView(FormView):
    form_class = AppointmentConfirmForm
    # template_name = 'appointments/book_appointment.html' # TODO: بعداً اضافه شود
    
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
# ایدی تایم اسلات رو میگیریم
        self.time_slot = get_object_or_404(TimeSlot, pk=kwargs.get('slot_id'))

    def form_valid(self, form):
# برسی میکنیم که پر نباشه
        if self.time_slot.status != 'available':
            messages.error(self.request, "این زمان قبلاً رزرو شده است.")
            return redirect('doctor_detail', pk=self.time_slot.doctor.id)
        # پیدا کردن بیمار در فاز ۲ این خط جایگزین میشه
        patient = Patient.objects.first()
        #ساخت نوبت با وضعیت اولیه
        appointment = Appointment.objects.create(
            patient=patient,
            time_slot=self.time_slot,
            price=self.time_slot.doctor.consultation_fee,
            status='pending'
        )
        # تغییر وضعیت اسلات به رزرو شده
        self.time_slot.status = 'booked'
        self.time_slot.save()

        # faeze (T4.3)
        # TODO: بعد از تکمیل تسک فائزه این بخش کامل میشه و پیشنهادی و حدودی میشه این شکلی فکر میکنم   
        try:
            # from payments.services import pay_for_appointment
            # is_paid = pay_for_appointment(patient, appointment.price)
            is_paid = True  # الان فرض میکنیم که پرداخت درست بوده
            if is_paid:
                appointment.status = 'confirmed'
                appointment.save()
                messages.success(self.request, "نوبت شما با موفقیت رزرو و پرداخت شد.")
            else:
                messages.warning(self.request, "رزرو انجام شد اما پرداخت ناموفق بود. وضعیت: در انتظار پرداخت.")
        except Exception:
            pass

        # ریدایرکت به صفحه نوبت‌های من (faeze) یا فعلاً همون صفحه پزشک
        return redirect('doctor_detail', pk=self.time_slot.doctor.id)

# TASK T3.3 (Mahyar) 
class AppointmentCancelView(UpdateView):
    model = Appointment
    # template_name = 'appointments/cancel_appointment.html' # TODO: بعداً اضافه شود
    fields = [] 
    
    def form_valid(self, form):
        appointment = self.get_object()
# بررسی اینکه نوبت قابل لغو باشه
        if appointment.status in ['pending', 'confirmed']:
# تغییر وضعیت تایم اسلات
            appointment.status = 'canceled'
            appointment.save()
# تغییر وضعیت تایم اسلات به حالت آزاد
            appointment.time_slot.status = 'available'
            appointment.time_slot.save()
            messages.success(self.request, "نوبت شما با موفقیت لغو شد.")
        else:
            messages.error(self.request, "این نوبت قابل لغو نیست.")
            
        return redirect('doctor_detail', pk=appointment.time_slot.doctor.id)