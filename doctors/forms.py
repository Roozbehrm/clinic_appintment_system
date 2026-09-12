from django import forms
from django.utils.crypto import get_random_string

from accounts.forms import phone_validator
from accounts.models import Profile, User
from accounts.services import send_new_account_credentials

from .models import WorkingHour, Doctor


class WorkingHourForm(forms.ModelForm):
    class Meta:
        model = WorkingHour
        fields = ["day_of_week", "start_time", "end_time", "slot_duration_minutes"]
        widgets = {
            "day_of_week": forms.Select(attrs={"class": "form-select"}),
            "start_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "end_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "slot_duration_minutes": forms.NumberInput(attrs={"class": "form-control", "min": 5, "step": 5}),
        }

    def __init__(self, *args, doctor=None, **kwargs):

        self.doctor = doctor
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        day = cleaned.get("day_of_week")
        start = cleaned.get("start_time")
        end = cleaned.get("end_time")

        if start and end and start >= end:
            raise forms.ValidationError("ساعت شروع باید قبل از ساعت پایان باشد.")

        if self.doctor and day is not None and start and end:
            overlapping = WorkingHour.objects.filter(
                doctor=self.doctor, day_of_week=day,
                start_time__lt=end, end_time__gt=start,
            )
            if self.instance.pk:
                overlapping = overlapping.exclude(pk=self.instance.pk)
            if overlapping.exists():
                raise forms.ValidationError(
                    "این بازه با یکی از ساعات کاری قبلی همین روز همپوشانی دارد."
                )
        return cleaned


class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ["specialty", "bio", "consultation_fee", "is_active"]
        widgets = {
            "specialty": forms.Select(attrs={"class": "form-select"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "consultation_fee": forms.NumberInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class DoctorSearchForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "جستجو بر اساس نام پزشک..."}))
    specialty = forms.CharField(required=False, widget=forms.HiddenInput())


class DoctorCreationForm(forms.ModelForm):
    """
    فرم افزودن پزشک جدید، مخصوص پنل ادمین (کارمند).

    قبلاً کارمند برای ساختن یک پزشک باید ۳ مرحله‌ی جدا طی می‌کرد (کاربر
    در accounts › Users، بعد پروفایل، بعد پزشک) — که چون کاربرها با
    شماره تلفن لیست می‌شدند، پیدا کردن رکورد درست گیج‌کننده بود. این
    فرم هر سه مرحله (User + Profile + Doctor) را در یک صفحه انجام می‌دهد.
    """
    phone_number = forms.CharField(label="شماره تلفن پزشک", validators=[phone_validator])
    email = forms.EmailField(label="ایمیل پزشک")
    full_name = forms.CharField(label="نام و نام خانوادگی پزشک")
    password = forms.CharField(
        label="رمز عبور اولیه (خالی بگذارید تا خودکار ساخته شود — در هر دو حالت با پیامک/ایمیل به خود پزشک اطلاع داده می‌شود)",
        widget=forms.PasswordInput, required=False,
    )

    class Meta:
        model = Doctor
        fields = ["specialty", "bio", "consultation_fee", "is_active"]

    def clean_phone_number(self):
        phone = self.cleaned_data["phone_number"]
        if User.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError("کاربری با این شماره تلفن از قبل وجود دارد.")
        return phone

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("کاربری با این ایمیل از قبل وجود دارد.")
        return email

    def save(self, commit=True):
        doctor = super().save(commit=False)

        password = self.cleaned_data["password"] or get_random_string(10)
        user = User.objects.create_user(
            phone_number=self.cleaned_data["phone_number"],
            email=self.cleaned_data["email"],
            password=password,
            is_verified=True,
        )
        profile = Profile.objects.create(user=user, full_name=self.cleaned_data["full_name"])
        doctor.profile = profile

        send_new_account_credentials(user, password)

        self.generated_password = password

        if commit:
            doctor.save()
        return doctor
