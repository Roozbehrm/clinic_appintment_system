from django.urls import path
from . import views

app_name = 'accounts'


app_name = "accounts"

urlpatterns = [
    # TASK T5.4 (Mahyar) 
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('redirect/', views.RedirectAfterLoginView.as_view(), name='redirect_after_login'),
    # TASK T5.8 (Mahyar) 
    path('complete-profile/', views.CompleteProfileView.as_view(), name='complete_profile'),
    path('verify-otp/', views.VerifyOTPView.as_view(), name='verify_otp'),
    path("register/", views.RegisterView.as_view(), name="register"),
    path('otp-login/', views.OTPLoginRequestView.as_view(), name = 'otp_login'),
    
]
