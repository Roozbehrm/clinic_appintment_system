from django.contrib import messages
from django.shortcuts import redirect


class DoctorRequiredMixin:
    """فقط کاربرانی که نقش پزشک دارند اجازه‌ی دسترسی دارند."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_doctor:
            messages.error(request, "دسترسی غیرمجاز.")
            return redirect("accounts:login")
        return super().dispatch(request, *args, **kwargs)
from django.contrib import messages
from django.shortcuts import redirect


class DoctorRequiredMixin:
  # users with the doctor role are allowed access only.

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_doctor:
            messages.error(request, "دسترسی غیرمجاز.")
            return redirect("accounts:login")
        return super().dispatch(request, *args, **kwargs)
