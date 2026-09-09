from django import forms
from .models import Patient


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["birth_date"]
        widgets = {
            "birth_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }