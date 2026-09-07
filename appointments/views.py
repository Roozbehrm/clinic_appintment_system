from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, get_object_or_404
from django.views import View
from doctors.models import TimeSlot
from .models import Appointment
from .services import book_appointment, cancel_appointment


# TASK T3.3 (Mahyar)
class BookAppointmentView(LoginRequiredMixin, View):
    # آدرس صفحه لاگین که اگر کاربر لاگین نبود بره اونجا
    login_url = "accounts:login"

    def post(self, request, time_slot_id):
# برسی نقش که بیمار هست یا خیر
        if not getattr(request.user, 'is_patient', False):
            messages.error(request, "فقط بیماران مجاز به رزرو نوبت هستند.")
        # اگر بیمار نبود برش می‌گردونیم به صفحه اصلی
            return redirect('home')

        # گرفتن اسلات برای پیدا کردن آیدی پزشک
        slot = get_object_or_404(TimeSlot, pk=time_slot_id)

        try:
# پیدا کردن پروفایل بیمار
            patient = request.user.profile.patient
            
            book_appointment(patient, time_slot_id)
            
            messages.success(request, "نوبت شما با موفقیت رزرو شد.")
            return redirect('patients:my_appointments')
        except ValidationError as e:
            messages.error(request, e.message if hasattr(e, 'message') else str(e))
            return redirect('doctors:detail', pk=slot.doctor.id)
        except Exception as e:
            messages.error(request, "خطایی در سیستم رخ داد. لطفا دوباره تلاش کنید.")
            return redirect('doctors:detail', pk=slot.doctor.id)


class CancelAppointmentView(LoginRequiredMixin, View):
    login_url = "accounts:login"

    def post(self, request, pk):
        try:
            # پیدا کردن پروفایل بیمار
            patient = request.user.profile.patient
            
            # پیدا کردن نوبتی که هم آیدیش درست باشه هم مال همین بیمار باش
            appointment = get_object_or_404(Appointment, pk=pk, patient=patient)

        # تابع سرویس لغو
            cancel_appointment(appointment)
            
            messages.success(request, "نوبت شما با موفقیت لغو شد.")

        except ValidationError as e:
            messages.error(request, e.message if hasattr(e, 'message') else str(e))
        except Exception:
            messages.error(request, "خطایی در لغو نوبت رخ داد.")

        # در هر صورت برمی‌گرده به صفحه نوبت‌های من
        return redirect('patients:my_appointments')