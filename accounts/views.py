from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View

from .forms import LoginForm, ProfileForm
from .services import issue_otp

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