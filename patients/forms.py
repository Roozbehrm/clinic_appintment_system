
import jdatetime
from django import forms

from .models import Patient


class PatientForm(forms.ModelForm):

    birth_date = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "مثلاً 1375/04/20",
                "dir": "ltr",
            }
        )
    )

    class Meta:
        model = Patient
        fields = ["birth_date"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.birth_date:
            self.initial["birth_date"] = jdatetime.date.fromgregorian(
                date=self.instance.birth_date
            ).strftime("%Y/%m/%d")

    def clean_birth_date(self):
        value = self.cleaned_data.get("birth_date")

        if not value:
            return None

        try:
            year, month, day = map(
                int,
                value.replace("-", "/").split("/")
            )

            return jdatetime.date(
                year,
                month,
                day
            ).togregorian()

        except (ValueError, TypeError):
            raise forms.ValidationError(
                "تاریخ تولد را به صورت 1400/01/15 وارد کنید."
            )

