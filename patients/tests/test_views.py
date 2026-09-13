from datetime import date, timedelta

import pytest
from django.urls import reverse

from appointments.models import Appointment


@pytest.mark.django_db
class TestMyAppointmentsView:
    def test_requires_login(self, client):
        response = client.get(reverse("patients:my_appointments"))
        assert response.status_code == 302

    def test_shows_only_own_appointments(self, client, patient_user, doctor_user, free_time_slot):
        appointment = Appointment.objects.create(
            patient=patient_user, time_slot=free_time_slot,
            price=200000, status="confirmed",
        )
        client.force_login(patient_user.profile.user)
        response = client.get(reverse("patients:my_appointments"))

        assert response.status_code == 200
        assert list(response.context["appointments"]) == [appointment]

    def test_past_confirmed_appointment_is_auto_completed_on_view(
        self, client, patient_user, doctor_user
    ):
        from doctors.models import TimeSlot

        past_slot = TimeSlot.objects.create(
            doctor=doctor_user,
            visit_date=date.today() - timedelta(days=1),
            start_time="09:00",
            end_time="09:30",
            status="booked",
        )
        appointment = Appointment.objects.create(
            patient=patient_user, time_slot=past_slot,
            price=200000, status="confirmed",
        )

        client.force_login(patient_user.profile.user)
        client.get(reverse("patients:my_appointments"))

        appointment.refresh_from_db()
        assert appointment.status == "completed"
