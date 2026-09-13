import pytest
from django.urls import reverse

from accounts.models import Profile, User
from appointments.models import Appointment
from patients.models import Patient
from payments.models import Wallet

TEST_PASSWORD = "StrongPass123!"


@pytest.mark.django_db
class TestBookAppointmentView:
    def test_anonymous_user_is_redirected_to_login(self, client, free_time_slot):
        response = client.post(reverse("appointments:book", args=[free_time_slot.id]))
        assert response.status_code == 302
        assert "login" in response.url

    def test_patient_can_book_a_free_slot(self, client, patient_user, free_time_slot):
        client.force_login(patient_user.profile.user)

        response = client.post(reverse("appointments:book", args=[free_time_slot.id]))

        assert response.status_code == 302
        assert response.url == reverse("patients:my_appointments")
        assert Appointment.objects.filter(patient=patient_user, time_slot=free_time_slot).exists()

    def test_doctor_account_cannot_book_an_appointment(self, client, doctor_user, free_time_slot):
        client.force_login(doctor_user.profile.user)

        response = client.post(reverse("appointments:book", args=[free_time_slot.id]))

        assert response.status_code == 302
        assert response.url == reverse("doctors:search")
        assert not Appointment.objects.filter(time_slot=free_time_slot).exists()

    def test_booking_a_taken_slot_redirects_back_to_doctor_page(
        self, client, patient_user, doctor_user, free_time_slot
    ):
        free_time_slot.status = "booked"
        free_time_slot.save()

        client.force_login(patient_user.profile.user)
        response = client.post(reverse("appointments:book", args=[free_time_slot.id]))

        assert response.status_code == 302
        assert response.url == reverse("doctors:detail", args=[doctor_user.pk])


@pytest.mark.django_db
class TestCancelAppointmentView:
    def test_owner_can_cancel_their_confirmed_appointment(self, client, patient_user, free_time_slot):
        free_time_slot.status = "booked"
        free_time_slot.save()
        appointment = Appointment.objects.create(
            patient=patient_user, time_slot=free_time_slot, price=200000, status="confirmed",
        )

        client.force_login(patient_user.profile.user)
        response = client.post(reverse("appointments:cancel", args=[appointment.pk]))

        assert response.status_code == 302
        appointment.refresh_from_db()
        assert appointment.status == "cancelled"

    def test_a_stranger_cannot_cancel_someone_elses_appointment(self, client, free_time_slot):
        owner_user = User.objects.create(phone_number="09145555555", email="owner@example.com", is_verified=True)
        owner_profile = Profile.objects.create(user=owner_user, full_name="بیمار اصلی")
        owner_patient = Patient.objects.create(profile=owner_profile)
        Wallet.objects.create(patient=owner_patient, balance=1000000)

        stranger_user = User.objects.create(phone_number="09146666666", email="stranger@example.com", is_verified=True)
        stranger_user.set_password(TEST_PASSWORD)
        stranger_user.save()
        stranger_profile = Profile.objects.create(user=stranger_user, full_name="غریبه")
        Patient.objects.create(profile=stranger_profile)

        appointment = Appointment.objects.create(
            patient=owner_patient, time_slot=free_time_slot, price=200000, status="confirmed",
        )

        client.force_login(stranger_user)
        response = client.post(reverse("appointments:cancel", args=[appointment.pk]))

        assert response.status_code == 404
        appointment.refresh_from_db()
        assert appointment.status == "confirmed"