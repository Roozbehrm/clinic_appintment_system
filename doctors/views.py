from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views import View

from accounts.forms import LoginForm

from .forms import DoctorProfileForm, DoctorSearchForm, WorkingHourForm
from .mixin import DoctorRequiredMixin
from .models import Doctor, Specialty, TimeSlot, WorkingHour
from .services import generate_time_slots


class DoctorLoginView(View):
    template_name = "doctors/login.html"

    def get(self, request):
        form = LoginForm()

        return render(
            request,
            self.template_name,
            {"form": form},
        )

    def post(self, request):
        form = LoginForm(request.POST)

        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {"form": form},
            )

        phone_number = form.cleaned_data["phone_number"]
        password = form.cleaned_data["password"]

        user = authenticate(
            request,
            username=phone_number,
            password=password,
        )

        if user is None:
            messages.error(
                request,
                "شماره تلفن یا رمز عبور اشتباه است.",
            )

            return render(
                request,
                self.template_name,
                {"form": form},
            )

        if not user.is_doctor:
            messages.error(
                request,
                "این حساب پزشک نیست.",
            )

            return render(
                request,
                self.template_name,
                {"form": form},
            )

        if not user.is_verified:
            messages.error(
                request,
                "حساب پزشک هنوز تایید نشده است.",
            )

            return render(
                request,
                self.template_name,
                {"form": form},
            )

        login(request, user)

        return redirect("doctors:dashboard")


class DashboardView(
    LoginRequiredMixin,
    DoctorRequiredMixin,
    View,
):
    login_url = "accounts:login"

    def get(self, request):
        doctor = get_object_or_404(
            Doctor.objects.select_related(
                "profile",
                "specialty",
            ),
            profile__user=request.user,
        )

        from appointments.models import Appointment

        today = timezone.localdate()

        upcoming = (
            Appointment.objects.filter(
                time_slot__doctor=doctor,
                status="confirmed",
                time_slot__visit_date__gte=today,
            )
            .select_related(
                "patient",
                "time_slot",
            )
            .order_by(
                "time_slot__visit_date",
                "time_slot__start_time",
            )
        )

        total_slots = TimeSlot.objects.filter(
            doctor=doctor,
        ).count()

        free_slots = TimeSlot.objects.filter(
            doctor=doctor,
            status=TimeSlot.STATUS_FREE,
        ).count()

        booked_slots = TimeSlot.objects.filter(
            doctor=doctor,
            status=TimeSlot.STATUS_BOOKED,
        ).count()

        stats = {
            "total_slots": total_slots,
            "free_slots": free_slots,
            "booked_slots": booked_slots,
            "average_rating": doctor.average_rating,
            "review_count": doctor.review_count,
        }

        return render(
            request,
            "doctors/dashboard.html",
            {
                "doctor": doctor,
                "upcoming": upcoming,
                "stats": stats,
            },
        )


class ProfileSettingsView(LoginRequiredMixin, View):
    login_url = "accounts:login"
    template_name = "doctors/profile_settings.html"

    def get_doctor(self, request):
        return get_object_or_404(
            Doctor.objects.select_related(
                "profile",
                "specialty",
            ),
            profile__user=request.user,
        )

    def get(self, request):
        doctor = self.get_doctor(request)

        form = DoctorProfileForm(
            instance=doctor,
        )

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "doctor": doctor,
            },
        )

    def post(self, request):
        doctor = self.get_doctor(request)

        form = DoctorProfileForm(
            request.POST,
            instance=doctor,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "اطلاعات پروفایل با موفقیت ذخیره شد.",
            )

            return redirect("doctors:profile_settings")

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "doctor": doctor,
            },
        )


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


class GenerateSlotsView(LoginRequiredMixin, View):
    login_url = "accounts:login"

    def post(self, request):
        doctor = get_object_or_404(
            Doctor,
            profile__user=request.user,
        )

        created_count = generate_time_slots(
            doctor,
            days_ahead=14,
        )

        if created_count:
            messages.success(
                request,
                f"{created_count} اسلات جدید ساخته شد.",
            )
        else:
            messages.info(
                request,
                "چیز جدیدی برای ساخت وجود نداشت.",
            )

        return redirect(
            "doctors:manage_slots",
        )


class ManageSlotsView(LoginRequiredMixin, View):
    login_url = "accounts:login"
    template_name = "doctors/manage_slots.html"

    def get(self, request):
        doctor = get_object_or_404(
            Doctor,
            profile__user=request.user,
        )

        from appointments.services import (
            auto_complete_past_appointments,
        )

        auto_complete_past_appointments(
            doctor=doctor,
        )

        slots = (
            TimeSlot.objects.filter(
                doctor=doctor,
            )
            .select_related("working_hours")
            .order_by(
                "-visit_date",
                "-start_time",
            )[:100]
        )

        return render(
            request,
            self.template_name,
            {
                "doctor": doctor,
                "slots": slots,
            },
        )


class CompleteAppointmentView(LoginRequiredMixin, View):
    pass
