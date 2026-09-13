import pytest
from django.urls import reverse

from appointments.models import Appointment
from reviews.models import Review


@pytest.mark.django_db
class TestAddReviewView:
    def test_can_review_completed_appointment(self, client, patient_user, free_time_slot):
        appointment = Appointment.objects.create(
            patient=patient_user, time_slot=free_time_slot, price=200000, status="completed",
        )
        client.force_login(patient_user.profile.user)

        response = client.post(reverse("reviews:add_review", args=[appointment.pk]), {
            "rating": 5,
            "comment": "عالی بود",
        })

        assert response.status_code == 302
        assert response.url == reverse("patients:my_appointments")
        review = Review.objects.get(appointment=appointment)
        assert review.rating == 5
        assert review.comment == "عالی بود"

    def test_cannot_review_non_completed_appointment(self, client, patient_user, free_time_slot):
        appointment = Appointment.objects.create(
            patient=patient_user, time_slot=free_time_slot, price=200000, status="confirmed",
        )
        client.force_login(patient_user.profile.user)

        response = client.get(reverse("reviews:add_review", args=[appointment.pk]))

        assert response.status_code == 302
        assert response.url == reverse("patients:my_appointments")
        assert not Review.objects.filter(appointment=appointment).exists()

    def test_cannot_review_same_appointment_twice(self, client, patient_user, free_time_slot):
        appointment = Appointment.objects.create(
            patient=patient_user, time_slot=free_time_slot, price=200000, status="completed",
        )
        Review.objects.create(appointment=appointment, rating=3, comment="اولین نظر")
        client.force_login(patient_user.profile.user)

        response = client.get(reverse("reviews:add_review", args=[appointment.pk]))

        # چون appointment.is_reviewable وقتی review از قبل وجود دارد False می‌شود
        assert response.status_code == 302
        assert Review.objects.filter(appointment=appointment).count() == 1

    def test_other_patients_appointment_returns_404(self, client, doctor_user, free_time_slot):
        from accounts.models import User, Profile
        from patients.models import Patient
        from payments.models import Wallet

        owner_user = User.objects.create(phone_number="09147777777", email="owner2@example.com", is_verified=True)
        owner_profile = Profile.objects.create(user=owner_user, full_name="صاحب نوبت")
        owner_patient = Patient.objects.create(profile=owner_profile)
        Wallet.objects.create(patient=owner_patient, balance=1000000)

        stranger_user = User.objects.create(phone_number="09148888888", email="stranger2@example.com", is_verified=True)
        stranger_profile = Profile.objects.create(user=stranger_user, full_name="غریبه")
        Patient.objects.create(profile=stranger_profile)

        appointment = Appointment.objects.create(
            patient=owner_patient, time_slot=free_time_slot, price=200000, status="completed",
        )

        client.force_login(stranger_user)
        response = client.get(reverse("reviews:add_review", args=[appointment.pk]))

        assert response.status_code == 404
