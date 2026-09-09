from django import forms

# TASK T3.3 (Mahyar)
class AppointmentConfirmForm(forms.Form):
# نیازی به فیلد نداره و فقط برای امنیت پست ارسالی هست
    confirm = forms.BooleanField(initial=True, widget=forms.HiddenInput())