from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404, render
from django.views import View

from appointments.models import Appointment
from .forms import ReviewForm


class AddReviewView(LoginRequiredMixin, View):
    login_url = "accounts:login"
    template_name = "reviews/add_review.html"

    def get(self, request, appointment_id):
        appointment = get_object_or_404(
            Appointment, pk=appointment_id, patient=request.user.profile.patient)
        if not appointment.is_reviewable:
            messages.error(request, "امکان ثبت نظر برای این نوبت وجود ندارد.")
            return redirect("patients:my_appointments")
        form = ReviewForm()
        return render(request, self.template_name, {"form": form, "appointment": appointment})


    def post(self, request, appointment_id):
        appointment = get_object_or_404(
            Appointment, pk=appointment_id, patient=request.user.profile.patient)
        if not appointment.is_reviewable:
            messages.error(request, "امکان ثبت نظر برای این نوبت وجود ندارد.")
            return redirect("patients:my_appointments")


        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.appointment = appointment
            review.save()
            messages.success(request, "نظر شما ثبت شد. سپاسگزاریم!")
            return redirect("patients:my_appointments")
        return render(request, self.template_name, {"form": form, "appointment": appointment})
