from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("register/quick/", views.QuickRegisterView.as_view(), name="quick_register"),
    path("verify-otp/", views.VerifyOTPView.as_view(), name="verify_otp"),
    path("resend-otp/", views.ResendOTPView.as_view(), name="resend_otp"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("login/otp/", views.OTPLoginRequestView.as_view(), name="otp_login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("after-login/", views.RedirectAfterLoginView.as_view(), name="redirect_after_login"),
    path("password/change/", views.ChangePasswordView.as_view(), name="change_password"),
    path("password-reset/", views.RequestPasswordResetView.as_view(), name="request_reset"),
    path("password-reset/email/", views.RequestPasswordResetByEmailView.as_view(), name="request_reset_email"),
    path("password-reset/confirm/<uidb64>/<token>/", views.ResetPasswordWithTokenView.as_view(), name="reset_with_token"),
    path("set-new-password/", views.SetNewPasswordView.as_view(), name="set_new_password"),
    path("complete-profile/", views.CompleteProfileView.as_view(), name="complete_profile"),
]
