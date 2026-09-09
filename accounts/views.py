import random
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from accounts.forms import PhoneOnlyForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import (RegisterForm, OTPVerifyForm, LoginForm, ProfileForm,
                     RequestPasswordResetForm, SetNewPasswordForm, PhoneOnlyForm)
from .services import issue_otp , find_user_by_identifier
from django.contrib.auth import get_user_model
from .models import User, OTP, Profile



class OTPLoginRequestView(View):

    def get(self,request):

        form = PhoneOnlyForm()

        return render(
            request,
            'accounts/otp_login.html',
            {'form':form}
        )

    def post(self,request):

        form = PhoneOnlyForm(request.POST)

        if form.is_valid():

            phone = form.cleaned_data.get('phone_number')
            try:
                user = User.objects.get(phone_number = phone)

            except User.DoesNotExist:

                form.add_error(
                    'phone_number', 'کاربری با این شماره موبایل وجود ندارد')

                return render(request,
                            'accounts/otp_login.html',
                          {'form':form})
                
            code = str(
                random.randint(100000,999999)
                )
                
            OTP.objects.create(
                user_id = user.id,
                code = code,
                purpose = 'otp_login',
                expires_at = timezone.now() + timedelta(
                    minutes= settings.OTP_EXPIRY_MINUTES 
                )
            )

            return redirect('accounts:verify_otp')
        
        return render(
            request,
            'accounts/otp_login.html',
            {'form': form}
        )

      
# TASK T5.4 (Mahyar)
class LoginView(View):
    template_name = "accounts/login.html"

    def get(self, request):
        # اگه کاربر از قبل لاگین بود، بفرستش به صفحه بعد از ورود
        if request.user.is_authenticated:
            return redirect('accounts:redirect_after_login')
            
        form = LoginForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data.get('phone_number')
            password = form.cleaned_data.get('password')
            # احراز هویت با استفاده از متد پیش‌فرض جنگو
            user = authenticate(request, username=phone_number, password=password)
            if user is not None:
                # بررسی اینکه آیا کاربر پزشک است یا خیر 
                # (getattr استفاده می‌کنیم تا اگر فیلد نبود ارور ندهد)
                if getattr(user, 'is_doctor', False):
                    messages.error(request, "پزشکان باید از صفحه‌ی ورود مخصوص پزشکان وارد شوند.")
                    return redirect('doctors:login')
        
                # بررسی تایید شماره موبایل (OTP)
                if not getattr(user, 'is_verified', False):
                    issue_otp(user, "login")
                    request.session['auth_phone'] = phone_number
                    messages.warning(request, "حساب شما تایید نشده است. لطفاً کد پیامک شده را وارد کنید.")
                    return redirect('accounts:verify_otp')
                
                login(request, user)
                messages.success(request, "با موفقیت وارد شدید.")
                return redirect('accounts:redirect_after_login')
            else:
                messages.error(request, "شماره تلفن یا رمز عبور اشتباه است.")
                
        return render(request, self.template_name, {"form": form})


class RedirectAfterLoginView(LoginRequiredMixin, View):
    login_url = "accounts:login"

    def get(self, request):
        user = request.user
        # مسیریابی بر اساس نقش کاربر
        if user.is_staff:
            return redirect('/admin/')
        elif getattr(user, 'is_doctor', False):
            return redirect('doctors:dashboard')
        elif getattr(user, 'is_patient', False):
            return redirect('doctors:search')
        else:
            # کاربری که پروفایلش ناقصه یا نقش نداره
            return redirect('accounts:complete_profile')


class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, "با موفقیت خارج شدید.")
        return redirect('accounts:login')



# TASK T5.8 (Mahyar)
class CompleteProfileView(LoginRequiredMixin, View):
    login_url = "accounts:login"
    template_name = "accounts/complete_profile.html"

    def get(self, request):
        # نمایش فرم با دیتای فعلی پروفایل کاربر
        form = ProfileForm(instance=request.user.profile)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, "پروفایل شما با موفقیت تکمیل شد.")
            return redirect('accounts:redirect_after_login')
            
        return render(request, self.template_name, {"form": form})


# TASK T5.3 (Mahyar)
User = get_user_model()
class VerifyOTPView(View):
    template_name = "accounts/verify_otp.html"

    def get(self, request):
        # اگر شماره‌ای تو سشن نبود یعنی کاربر از صفحه لاگین نیومده
        if 'auth_phone' not in request.session:
            messages.error(request, "ابتدا شماره تلفن خود را وارد کنید.")
            return redirect('accounts:login')
            
        form = OTPVerifyForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        if 'auth_phone' not in request.session:
            return redirect('accounts:login')
            
        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            phone = request.session['auth_phone']
            code = form.cleaned_data.get('code')
            
            try:
                user = User.objects.get(phone_number=phone)
                
                # (T5.1 )
                # TODO: بعد مرج از کامنت در میاریم
                # from .services import verify_otp_code
                # is_valid = verify_otp_code(user, code)
                is_valid = True  
                
                if is_valid:
                    # تایید کردن حساب کاربر
                    user.is_verified = True
                    user.save()
                    
                    # لاگین کردن کاربر
                    login(request, user)
                    
                    # پاک کردن شماره از سشن
                    del request.session['auth_phone']
                    
                    messages.success(request, "حساب شما با موفقیت تایید شد.")
                    return redirect('accounts:redirect_after_login')
                else:
                    messages.error(request, "کد وارد شده نامعتبر یا منقضی شده است.")
            except User.DoesNotExist:
                messages.error(request, "کاربری با این شماره یافت نشد.")
                return redirect('accounts:login')
                
        return render(request, self.template_name, {"form": form})


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
