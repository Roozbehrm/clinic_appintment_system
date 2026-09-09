from django.contrib import messages
from django.shortcuts import redirect


class DoctorRequiredMixin:

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_doctor:
            messages.error(
                request,
                "شما دسترسی به پنل پزشکان را ندارید.",
            )
            return redirect("accounts:login")

        return super().dispatch(request, *args, **kwargs)
