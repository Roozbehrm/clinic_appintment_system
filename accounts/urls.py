from django.urls import path
from accounts.views import OTPLoginRequestView

app_name = 'accounts'

urlpatterns = [
    path('otp-login/',
    OTPLoginRequestView.as_view(),
    name = 'otp_login'),
]