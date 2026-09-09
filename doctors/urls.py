from django.urls import path

from .views import SearchDoctorsView, WorkingHoursView, DeleteWorkingHourView

urlpatterns = [
    path("search/", SearchDoctorsView.as_view(), name="search"),
    path("working-hours/", WorkingHoursView.as_view(), name="working_hours"),
    path(
        "working_hours/<int:pk>/delete/",
        DeleteWorkingHourView.as_view(),
        name="delete_working_hour",
    ),
]
