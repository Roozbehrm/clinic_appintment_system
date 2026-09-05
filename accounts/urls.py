from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("password-reset/", views.RequestPasswordResetView.as_view(), name="request_reset"),
    path("set-new-password/", views.SetNewPasswordView.as_view(), name="set_new_password"),
]
