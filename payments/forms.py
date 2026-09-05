from django import forms

class WalletTopUpForm(forms.Form):
    amount = forms.DecimalField(
        label = ' مبلغ افزایش موجودی',
        min_value = 1000,
        decimal_places=0,
        max_digits = 12
    )
