from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from .forms import DoctorSearchForm
from .models import Doctor, Specialty


class SearchDoctorsView(View):

    def get(self, request):
        form = DoctorSearchForm(request.GET)

        doctors = Doctor.objects.filter(is_active=True).select_related(
            "profile",
            "specialty",
        )

        q = request.GET.get("q", "").strip()
        specialty_id = request.GET.get("specialty", "").strip()

        if q:
            doctors = doctors.filter(profile__full_name__icontains=q) | doctors.filter(
                specialty__name__icontains=q
            )

        if specialty_id:
            doctors = doctors.filter(specialty_id=specialty_id)

        specialties = Specialty.objects.all()

        selected_specialty = specialty_id

        return render(
            request,
            "doctors/search.html",
            {
                "form": form,
                "doctors": doctors,
                "specialties": specialties,
                "selected_specialty": selected_specialty,
            },
        )
