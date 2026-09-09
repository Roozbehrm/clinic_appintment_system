from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views import View

from .forms import DoctorSearchForm, WorkingHourForm
from .models import Doctor, Specialty, TimeSlot, WorkingHour


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


class WorkingHoursView(LoginRequiredMixin, View):
    template_name = "doctors/working_hours.html"

    def get_doctor(self, request):
        return get_object_or_404(
            Doctor.objects.select_related("profile"),
            profile__user=request.user,
        )

    def get(self, request):
        doctor = self.get_doctor(request)

        form = WorkingHourForm()

        working_hours = doctor.working_hours.all().order_by(
            "day_of_week",
            "start_time",
        )

        today = timezone.localdate()

        future_slots = TimeSlot.objects.filter(
            doctor=doctor,
            visit_date__gte=today,
        ).order_by("visit_date", "start_time")[:200]

        slots_by_date = {}

        for slot in future_slots:
            slots_by_date.setdefault(slot.visit_date, []).append(slot)

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "doctor": doctor,
                "working_hours": working_hours,
                "slots_by_date": slots_by_date,
            },
        )

    def post(self, request):
        doctor = self.get_doctor(request)

        form = WorkingHourForm(request.POST)

        if form.is_valid():
            working_hour = form.save(commit=False)
            working_hour.doctor = doctor
            working_hour.save()

            messages.success(
                request,
                "ساعت کاری با موفقیت اضافه شد.",
            )

            return redirect("doctors:working_hours")

        working_hours = doctor.working_hours.all().order_by(
            "day_of_week",
            "start_time",
        )

        today = timezone.localdate()

        future_slots = TimeSlot.objects.filter(
            doctor=doctor,
            visit_date__gte=today,
        ).order_by("visit_date", "start_time")[:200]

        slots_by_date = {}

        for slot in future_slots:
            slots_by_date.setdefault(slot.visit_date, []).append(slot)

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "doctor": doctor,
                "working_hours": working_hours,
                "slots_by_date": slots_by_date,
            },
        )


class DeleteWorkingHourView(LoginRequiredMixin, View):

    def post(self, request, pk):
        working_hour = get_object_or_404(
            WorkingHour,
            pk=pk,
            doctor__profile__user=request.user,
        )

        working_hour.delete()

        messages.success(
            request,
            "ساعت کاری با موفقیت حذف شد.",
        )

        return redirect("doctors:working_hours")
