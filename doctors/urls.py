from django.urls import path

from .views import (
    SearchDoctorsView,
    WorkingHoursView,
    DeleteWorkingHourView,
    DoctorLoginView,
    DashboardView,
)

app_name = "doctors"

urlpatterns = [
    path("login/", DoctorLoginView.as_view(), name="login"),
    path("search/", SearchDoctorsView.as_view(), name="search"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("working-hours/", WorkingHoursView.as_view(), name="working_hours"),
    path(
        "working_hours/<int:pk>/delete/",
        DeleteWorkingHourView.as_view(),
        name="delete_working_hour",
    ),
]
