from django import forms

from .models import Doctor, Specialty, WorkingHour


class DoctorSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label="جستجو",
        widget=forms.TextInput(
            attrs={
                "placeholder": "نام پزشک یا تخصص را وارد کنید",
            }
        ),
    )

    specialty = forms.ModelChoiceField(
        queryset=Specialty.objects.all(),
        required=False,
        empty_label="همه تخصص ها",
        label="تخصص",
    )


class WorkingHourForm(forms.ModelForm):
    class Meta:
        model = WorkingHour
        fields = [
            "day_of_week",
            "start_time",
            "end_time",
            "slot_duration_minutes",
        ]
        widgets = {
            "start_time": forms.TimeInput(
                format="%H:%M",
                attrs={"type": "time"},
            ),
            "end_time": forms.TimeInput(
                format="%H:%M",
                attrs={"type": "time"},
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        slot_duration = cleaned_data.get("slot_duration_minutes")

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("ساعت پایان باید بعد از ساعت شروع باشد.")

        if slot_duration and slot_duration <= 0:
            raise forms.ValidationError("مدت زمان هر نوبت باید بیشتر از صفر باشد.")

        return cleaned_data


class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = [
            "specialty",
            "bio",
            "consultation_fee",
            "is_active",
        ]
