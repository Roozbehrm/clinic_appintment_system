from django import forms

from .models import Specialty


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
