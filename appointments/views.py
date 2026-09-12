from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, get_object_or_404
from django.views import View

from doctors.models import TimeSlot

from .models import Appointment
from .services import book_appointment, cancel_appointment


class BookAppointmentView(LoginRequiredMixin, View):
    login_url = "accounts:login"

    def post(self, request, time_slot_id):
        if not request.user.is_patient:
            messages.error(request, "فقط بیماران می‌توانند نوبت رزرو کنند.")
            return redirect("doctors:search")

        patient = request.user.profile.patient
        slot = get_object_or_404(TimeSlot, pk=time_slot_id)

        try:
            book_appointment(patient, time_slot_id)
            messages.success(request, "نوبت شما با موفقیت رزرو و تاییدیه ایمیل ارسال شد.")
        except ValidationError as e:
            messages.error(request, str(e.message) if hasattr(e, "message") else str(e))
            return redirect("doctors:detail", pk=slot.doctor_id)

        return redirect("patients:my_appointments")


class CancelAppointmentView(LoginRequiredMixin, View):
    login_url = "accounts:login"

    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk, patient=request.user.profile.patient)
        try:
            cancel_appointment(appointment)
            messages.success(request, "نوبت لغو و مبلغ به کیف پول بازگشت داده شد.")
        except ValidationError as e:
            messages.error(request, str(e))
        return redirect("patients:my_appointments")