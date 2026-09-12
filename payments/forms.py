from django import forms


class DepositForm(forms.Form):
    amount = forms.DecimalField(
        min_value=1000, max_digits=12, decimal_places=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "مبلغ به تومان"}))
