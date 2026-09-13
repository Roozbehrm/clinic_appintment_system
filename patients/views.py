from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from appointments.models import Appointment
from appointments.services import auto_complete_past_appointments


class MyAppointmentsView(LoginRequiredMixin, View):
    login_url = "accounts:login"

    def get(self, request):
        patient = request.user.profile.patient
        auto_complete_past_appointments(patient=patient)
        appointments = Appointment.objects.filter(patient=patient).select_related(
            "time_slot__doctor__profile").order_by("-created_at")
        return render(request, "patients/my_appointments.html", {"appointments": appointments})
