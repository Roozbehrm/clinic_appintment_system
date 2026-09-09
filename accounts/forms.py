from django import forms
from django.core.validators import RegexValidator
from .models import Profile

# یک ولیدیتور برای شماره تلفن موبایل ایران
phone_validator = RegexValidator(
    regex=r'^09\d{9}$',
    message="شماره تلفن باید با 09 شروع شده و 11 رقم باشد."
)


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