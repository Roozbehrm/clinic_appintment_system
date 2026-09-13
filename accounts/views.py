from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View

from .forms import (RegisterForm, QuickRegisterForm, OTPVerifyForm, LoginForm, ProfileForm,
                     ChangePasswordForm, RequestPasswordResetForm, RequestPasswordResetByEmailForm,
                     SetNewPasswordForm, PhoneOnlyForm)
from .models import User, OTP, Profile
from .services import issue_otp, find_user_by_identifier, send_new_account_credentials
from .tasks import send_email_task


class RegisterView(View):
    template_name = "accounts/register.html"

    def get(self, request):
        return render(request, self.template_name, {"form": RegisterForm()})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data["phone_number"]
            user, _ = User.objects.get_or_create(phone_number=phone, defaults={
                "email": form.cleaned_data["email"],
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


class QuickRegisterView(View):

    template_name = "accounts/quick_register.html"

    def get(self, request):
        return render(request, self.template_name, {"form": QuickRegisterForm()})

    def post(self, request):
        form = QuickRegisterForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data["phone_number"]
            email = form.cleaned_data["email"]
            temp_password = get_random_string(10)

            user, _ = User.objects.get_or_create(phone_number=phone, defaults={
                "email": email,
                "is_verified": False,
            })
            user.email = email
            user.set_password(temp_password)
            user.is_verified = False
            user.save()
            Profile.objects.get_or_create(user=user)

            from patients.models import Patient
            patient, _ = Patient.objects.get_or_create(profile=user.profile)
            from payments.models import Wallet
            Wallet.objects.get_or_create(patient=patient)

<<<<<<< HEAD

=======
>>>>>>> 445390f (Accounts: OTP, quick-register & avatar improvements)
            send_new_account_credentials(user, temp_password)
            issue_otp(user, "register")
            request.session["otp_user_id"] = user.id
            request.session["otp_purpose"] = "register"
            messages.info(request, "کد تایید و رمز عبور موقت برای شما ارسال شد (هم پیامک هم ایمیل).")
            return redirect("accounts:verify_otp")
        return render(request, self.template_name, {"form": form})


class VerifyOTPView(View):
    template_name = "accounts/verify_otp.html"

    def get(self, request):
        if not request.session.get("otp_user_id"):
            return redirect("accounts:register")
        return render(request, self.template_name, {"form": OTPVerifyForm()})

    def post(self, request):
        user_id = request.session.get("otp_user_id")
        purpose = request.session.get("otp_purpose")
        if not user_id:
            return redirect("accounts:register")
        user = get_object_or_404(User, id=user_id)
        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            otp = OTP.objects.filter(user=user, code=code, purpose=purpose, is_used=False).first()
            if otp and otp.is_valid():
                otp.is_used = True
                otp.save()
                if purpose in ("register", "login", "otp_login"):
                    user.is_verified = True
                    user.save()
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    del request.session["otp_user_id"]
                    del request.session["otp_purpose"]
                    messages.success(request, "خوش آمدید!")
                    return redirect("accounts:redirect_after_login")
                elif purpose == "reset_password":
                    request.session["reset_user_id"] = user.id
                    del request.session["otp_user_id"]
                    del request.session["otp_purpose"]
                    return redirect("accounts:set_new_password")
            messages.error(request, "کد وارد شده نامعتبر یا منقضی شده است.")
        return render(request, self.template_name, {"form": form})


class ResendOTPView(View):
    def get(self, request):
        user_id = request.session.get("otp_user_id")
        purpose = request.session.get("otp_purpose")
        channel = request.GET.get("via", "both")
        if channel not in ("both", "email"):
            channel = "both"
        if user_id and purpose:
            user = get_object_or_404(User, id=user_id)
            issue_otp(user, purpose, channel=channel)
            if channel == "email":
                messages.info(request, "کد جدید به ایمیل شما ارسال شد.")
            else:
                messages.info(request, "کد جدید ارسال شد.")
        return redirect("accounts:verify_otp")


class LoginView(View):

    template_name = "accounts/login.html"

    def get(self, request):
        return render(request, self.template_name, {"form": LoginForm()})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            target = find_user_by_identifier(form.cleaned_data["identifier"])
            user = None
            if target is not None:
   
                user = authenticate(request, username=target.email,
                                     password=form.cleaned_data["password"])
            if user is not None:
                if user.is_staff:
                    messages.error(
                        request,
                        "این حساب متعلق به کارمند/مدیر سیستم است. لطفاً از صفحه‌ی ورود پنل مدیریت (/admin) استفاده کنید.",
                    )
                    return render(request, self.template_name, {"form": form})
                if user.is_doctor:
                    messages.error(request, "این حساب متعلق به پزشک است. لطفاً از صفحه‌ی ورود پزشکان اقدام کنید.")
                    return render(request, self.template_name, {"form": form})
                if not user.is_verified:
                    issue_otp(user, "login")
                    request.session["otp_user_id"] = user.id
                    request.session["otp_purpose"] = "login"
                    return redirect("accounts:verify_otp")
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect("accounts:redirect_after_login")
            messages.error(request, "شماره تلفن/ایمیل یا رمز عبور اشتباه است.")
        return render(request, self.template_name, {"form": form})


class OTPLoginRequestView(View):

    template_name = "accounts/otp_login.html"

    def get(self, request):
        return render(request, self.template_name, {"form": PhoneOnlyForm()})

    def post(self, request):
        form = PhoneOnlyForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data["identifier"]
            user = find_user_by_identifier(identifier)
            if not user:
                messages.error(request, "کاربری با این شماره/ایمیل یافت نشد. ابتدا ثبت‌نام کنید.")
                return render(request, self.template_name, {"form": form})
            if user.is_staff:
                messages.error(
                    request,
                    "این حساب متعلق به کارمند/مدیر سیستم است. لطفاً از صفحه‌ی ورود پنل مدیریت (/admin) استفاده کنید.",
                )
                return render(request, self.template_name, {"form": form})
            if user.is_doctor:
                messages.error(request, "این حساب متعلق به پزشک است. لطفاً از صفحه‌ی ورود پزشکان اقدام کنید.")
                return render(request, self.template_name, {"form": form})
            issue_otp(user, "otp_login")
            request.session["otp_user_id"] = user.id
            request.session["otp_purpose"] = "otp_login"
            messages.info(request, "کد یکبار مصرف برای شما ارسال شد.")
            return redirect("accounts:verify_otp")
        return render(request, self.template_name, {"form": form})


class RedirectAfterLoginView(LoginRequiredMixin, View):
    login_url = "accounts:login"

    def get(self, request):
        user = request.user

        profile = getattr(user, "profile", None)
        if profile is not None and not profile.full_name.strip():
            return redirect("accounts:complete_profile")
        if user.is_staff:
            return redirect("/admin/")
        if user.is_doctor:
            return redirect("doctors:dashboard")
        if user.is_patient:
            return redirect("doctors:search")
        return redirect("accounts:complete_profile")


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("accounts:login")


class ChangePasswordView(LoginRequiredMixin, View):

    login_url = "accounts:login"
    template_name = "accounts/change_password.html"

    def get(self, request):
        return render(request, self.template_name, {"form": ChangePasswordForm(user=request.user)})

    def post(self, request):
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            request.user.set_password(form.cleaned_data["new_password"])
            request.user.save()
   
            update_session_auth_hash(request, request.user)
            messages.success(request, "رمز عبور با موفقیت تغییر کرد.")
            return redirect("accounts:redirect_after_login")
        return render(request, self.template_name, {"form": form})


class RequestPasswordResetView(View):
    template_name = "accounts/request_reset.html"

    def get(self, request):
        return render(request, self.template_name, {"form": RequestPasswordResetForm()})

    def post(self, request):
        form = RequestPasswordResetForm(request.POST)
        if form.is_valid():
            user = User.objects.filter(phone_number=form.cleaned_data["phone_number"]).first()
            if user:

                issue_otp(user, "reset_password", channel="sms")
                request.session["otp_user_id"] = user.id
                request.session["otp_purpose"] = "reset_password"
                return redirect("accounts:verify_otp")
            messages.error(request, "کاربری با این شماره یافت نشد.")
        return render(request, self.template_name, {"form": form})


class SetNewPasswordView(View):
    template_name = "accounts/set_new_password.html"

    def get(self, request):
        if not request.session.get("reset_user_id"):
            return redirect("accounts:request_reset")
        return render(request, self.template_name, {"form": SetNewPasswordForm()})

    def post(self, request):
        user_id = request.session.get("reset_user_id")
        if not user_id:
            return redirect("accounts:request_reset")
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            user = get_object_or_404(User, id=user_id)
            user.set_password(form.cleaned_data["password"])
            user.save()
            del request.session["reset_user_id"]
            messages.success(request, "رمز عبور با موفقیت تغییر کرد. اکنون وارد شوید.")
            return redirect("accounts:login")
        return render(request, self.template_name, {"form": form})


class RequestPasswordResetByEmailView(View):

    template_name = "accounts/request_reset_email.html"

    def get(self, request):
        return render(request, self.template_name, {"form": RequestPasswordResetByEmailForm()})

    def post(self, request):
        form = RequestPasswordResetByEmailForm(request.POST)
        if form.is_valid():
            user = User.objects.filter(email__iexact=form.cleaned_data["email"]).first()
            if user:
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_path = reverse("accounts:reset_with_token", kwargs={
                    "uidb64": uidb64, "token": token,
                })
                reset_url = request.build_absolute_uri(reset_path)
                try:
                    send_email_task.delay(
                        "بازیابی رمز عبور",
                        "برای تنظیم رمز عبور جدید روی لینک زیر بزنید:\n"
                        f"{reset_url}\n\nاگر این درخواست را شما نفرستاده‌اید، این ایمیل را نادیده بگیرید.",
                        [user.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass
<<<<<<< HEAD
 
=======

>>>>>>> 445390f (Accounts: OTP, quick-register & avatar improvements)
            messages.info(request, "اگر ایمیل واردشده در سیستم موجود باشد، لینک بازیابی برایش ارسال شد.")
            return redirect("accounts:login")
        return render(request, self.template_name, {"form": form})


class ResetPasswordWithTokenView(View):

    template_name = "accounts/set_new_password.html"

    def _get_user(self, uidb64):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            return User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None

    def get(self, request, uidb64, token):
        user = self._get_user(uidb64)
        if user is None or not default_token_generator.check_token(user, token):
            messages.error(request, "لینک بازیابی نامعتبر یا منقضی شده است.")
            return redirect("accounts:request_reset_email")
        return render(request, self.template_name, {"form": SetNewPasswordForm()})

    def post(self, request, uidb64, token):
        user = self._get_user(uidb64)
        if user is None or not default_token_generator.check_token(user, token):
            messages.error(request, "لینک بازیابی نامعتبر یا منقضی شده است.")
            return redirect("accounts:request_reset_email")
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data["password"])
            user.save()
            messages.success(request, "رمز عبور با موفقیت تغییر کرد. اکنون وارد شوید.")
            return redirect("accounts:login")
        return render(request, self.template_name, {"form": form})


class CompleteProfileView(LoginRequiredMixin, View):
    login_url = "accounts:login"
    template_name = "accounts/complete_profile.html"

    def get(self, request):
        form = ProfileForm(instance=request.user.profile)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, "پروفایل بروزرسانی شد.")
            return redirect("accounts:redirect_after_login")
        return render(request, self.template_name, {"form": form})
