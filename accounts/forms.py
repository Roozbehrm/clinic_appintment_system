from django import forms
from django.contrib.auth import password_validation
from django.core.validators import RegexValidator

from .models import User

phone_validator = RegexValidator(r"^09\d{9}$", "شماره تلفن معتبر نیست (مثال: 09123456789)")


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
