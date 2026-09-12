import pytest
from django.urls import reverse
from appointments.models import Appointment

@pytest.mark.django_db
class TestBookAppointmentView:
    def test_anonymous_user_redirected_to_login(self, client, free_time_slot):
        url = reverse("appointments:book", kwargs={"time_slot_id": free_time_slot.id})
        response = client.get(url)
        assert response.status_code == 302
        assert "login" in response.url

    def test_patient_can_book_successfully(self, client, patient_user, free_time_slot):
        user = patient_user.profile.user
        
        # شارژ کیف پول بیمار برای اینکه شرط موجودی در سرویس رزرو پاس شود
        patient_user.wallet.balance = 2000000
        patient_user.wallet.save()
        
        client.force_login(user)
        url = reverse("appointments:book", kwargs={"time_slot_id": free_time_slot.id})
        response = client.post(url)
        
        assert response.status_code == 302
        
        free_time_slot.refresh_from_db()
        assert free_time_slot.status == "booked"
        assert Appointment.objects.filter(patient=patient_user, time_slot=free_time_slot).exists()

@pytest.mark.django_db
class TestCancelAppointmentView:
    def test_anonymous_user_cannot_cancel(self, client, free_time_slot, patient_user):
        appointment = Appointment.objects.create(
            patient=patient_user,
            time_slot=free_time_slot,
            price=200000,
            status="confirmed",
        )
        url = reverse("appointments:cancel", kwargs={"pk": appointment.id})
        response = client.post(url)
        assert response.status_code == 302
        assert "login" in response.url

    def test_patient_can_cancel_own_appointment(self, client, patient_user, free_time_slot):
        user = patient_user.profile.user
        
        client.force_login(user)
        free_time_slot.status = "booked"
        free_time_slot.save()
        
        appointment = Appointment.objects.create(
            patient=patient_user,
            time_slot=free_time_slot,
            price=200000,
            status="confirmed",
        )
        
        url = reverse("appointments:cancel", kwargs={"pk": appointment.id})
        response = client.post(url)
        assert response.status_code == 302

        appointment.refresh_from_db()
        assert appointment.status == "cancelled"
        
        free_time_slot.refresh_from_db()
        assert free_time_slot.status == "free"