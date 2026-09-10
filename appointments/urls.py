from django.urls import path
from . import views

app_name = "appointments"

urlpatterns = [
    path("book/<int:time_slot_id>/", views.BookAppointmentView.as_view(), name="book"),   # مهیار T3.3
    path("<int:pk>/cancel/", views.CancelAppointmentView.as_view(), name="cancel"),        # مهیار T3.3
]