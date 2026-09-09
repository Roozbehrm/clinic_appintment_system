from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from .forms import (RegisterForm, OTPVerifyForm, LoginForm, ProfileForm,
                     RequestPasswordResetForm, SetNewPasswordForm, PhoneOnlyForm)
from .models import User, OTP, Profile
from .services import issue_otp, find_user_by_identifier

class RegisterView(View):
    template_name = "accounts/register.html"

    def get(self, request):
        return render(request, self.template_name, {"form": RegisterForm()})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data["phone_number"]
            user, _ = User.objects.get_or_create(phone_number=phone, defaults={
                "is_verified": False,
            })
            user.email = form.cleaned_data["email"]
            user.set_password(form.cleaned_data["password"])
            user.is_verified = False
            user.save()
            Profile.objects.get_or_create(user=user)

            from patients.models import Patient
            patient, _ = Patient.objects.get_or_create(profile=user.profile)
            from payments.models import Wallet
            Wallet.objects.get_or_create(patient=patient)

            issue_otp(user, "register")
            request.session["otp_user_id"] = user.id
            request.session["otp_purpose"] = "register"
            messages.info(request, "کد تایید برای شما ارسال شد.")
            return redirect("accounts:verify_otp")
        return render(request, self.template_name, {"form": form})


class ResendOTPView(View):
    def get(self, request):
        user_id = request.session.get("otp_user_id")
        purpose = request.session.get("otp_purpose")
        if user_id and purpose:
            user = get_object_or_404(User, id=user_id)
            issue_otp(user, purpose)
            messages.info(request, "کد جدید ارسال شد.")
        return redirect("accounts:verify_otp")