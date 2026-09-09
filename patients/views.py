
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View 

from appointments.models import Appointment
from appointments.services import auto_complete_past_appointments



class MyAppointmentsView(LoginRequiredMixin,View):

    login_url = "accounts:login"

    def get(self,request):

        patient = request.user.profile.patient

        auto_complete_past_appointments(patient=patient)

        appointments =  Appointment.objects.filter(
            patient_id = patient
            ).select_related(
              'time_slot_id',
              'time_slot_id__doctor_id__profile_id',
              'time_slot_id__doctor_id__specialty_id',
                ).order_by(
                '-created_at'
                )

        return render(
            request,
            'patients/my_appointments.html',
            {'appointments':appointments}
            )
         
