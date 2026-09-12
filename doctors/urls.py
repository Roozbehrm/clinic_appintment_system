from django.urls import path
from . import views

app_name = "doctors"

urlpatterns = [
    path("login/", views.DoctorLoginView.as_view(), name="login"),
    path("login/otp/", views.DoctorOTPLoginRequestView.as_view(), name="otp_login"),
    path("search/", views.SearchDoctorsView.as_view(), name="search"),
    path("<int:pk>/", views.DoctorDetailView.as_view(), name="detail"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("dashboard/profile/", views.ProfileSettingsView.as_view(), name="profile_settings"),
    path("dashboard/working-hours/", views.WorkingHoursView.as_view(), name="working_hours"),
    path("dashboard/working-hours/<int:pk>/delete/", views.DeleteWorkingHourView.as_view(), name="delete_working_hour"),
    path("dashboard/slots/<int:pk>/delete/", views.DeleteTimeSlotView.as_view(), name="delete_time_slot"),
    path("dashboard/generate-slots/", views.GenerateSlotsView.as_view(), name="generate_slots"),
    path("dashboard/slots/", views.ManageSlotsView.as_view(), name="manage_slots"),
    path("dashboard/appointments/<int:pk>/complete/", views.CompleteAppointmentView.as_view(), name="complete_appointment"),
]
