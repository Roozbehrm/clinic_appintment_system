from django import forms
from django.core.validators import RegexValidator
from .models import Profile , User
from django.contrib.auth import password_validation


class PhoneOnlyForm(forms.Form):

    phone_number = forms.CharField(
        max_length=11 , label = 'شماره موبایل'
        )

    def clean_phone_number(self):

        phone = self.cleaned_data.get('phone_number')

        if not phone.isdigit():
            raise forms.ValidationError ( 'شماره موبایل باید فقط شامل اعداد باشد.')

        if  len(phone) != 11:
            raise forms.ValidationError ( 'شماره موبایل باید ۱۱ رقم باشد.')


        if not phone.startwith('09'):
            raise forms.ValidationError ( 'شماره موبایل معتبر نیست.')

        return phone


# یک ولیدیتور برای شماره تلفن موبایل ایران

phone_validator = RegexValidator(r"^09\d{9}$", "شماره تلفن معتبر نیست (مثال: 09123456789)")

# TASK T5.4 (Mahyar)
class LoginForm(forms.Form):
    phone_number = forms.CharField(
        validators=[phone_validator],
        label="شماره تلفن",
        widget=forms.TextInput(attrs={'class': 'form-control text-start otp-input', 'placeholder': '09...', 'dir': 'ltr'})
    )
    password = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

# TASK T5.8 (Mahyar)
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["full_name", "avatar", "national_code", "gender", "address"]
        labels = {
            "full_name": "نام کامل",
            "avatar": "آواتار (اختیاری)",
            "national_code": "کد ملی",
            "gender": "جنسیت",
            "address": "آدرس",
        }
        # برای زیباتر شدن فرم در اچ تی ام ال
        widgets = {
            "full_name": forms.TextInput(attrs={'class': 'form-control'}),
            "national_code": forms.TextInput(attrs={'class': 'form-control'}),
            "gender": forms.Select(attrs={'class': 'form-select'}),
            "address": forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            "avatar": forms.FileInput(attrs={'class': 'form-control'}),
        }

# TASK T5.3 (Mahyar)    
class OTPVerifyForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        label="کد تایید",
        widget=forms.TextInput(attrs={
            'class': 'form-control otp-input text-center', 
            'placeholder': '------', 
            'dir': 'ltr'
        })
    )


class RegisterForm(forms.Form):
    phone_number = forms.CharField(validators=[phone_validator], widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "09123456789", "dir": "ltr"}))
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={"class": "form-control", "placeholder": "you@example.com", "dir": "ltr"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password") and cleaned.get("password_confirm"):
            if cleaned["password"] != cleaned["password_confirm"]:
                raise forms.ValidationError("رمز عبور و تکرار آن یکسان نیستند")
            password_validation.validate_password(cleaned["password"])
        return cleaned

    def clean_phone_number(self):
        phone = self.cleaned_data["phone_number"]
        if User.objects.filter(phone_number=phone, is_verified=True).exists():
            raise forms.ValidationError("این شماره قبلا ثبت‌نام کرده است")
        return phone

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email, is_verified=True).exists():
            raise forms.ValidationError("این ایمیل قبلاً استفاده شده است")
        return email


class RequestPasswordResetForm(forms.Form):
    phone_number = forms.CharField(validators=[phone_validator], widget=forms.TextInput(
        attrs={"class": "form-control", "dir": "ltr"}))


class SetNewPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password") != cleaned.get("password_confirm"):
            raise forms.ValidationError("رمز عبور و تکرار آن یکسان نیستند")
        if cleaned.get("password"):
            password_validation.validate_password(cleaned["password"])
        return cleaned
