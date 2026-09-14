import pytest
from django.urls import reverse

from accounts.models import OTP

PASSWORD = "StrongPass123!"


@pytest.mark.django_db
class TestDoctorLoginView:
    def test_doctor_can_login_with_phone(self, client, doctor_user):
        response = client.post(reverse("doctors:login"), {
            "identifier": doctor_user.profile.user.phone_number,
            "password": PASSWORD,
        })
        assert response.status_code == 302
        assert response.url == reverse("doctors:dashboard")

    def test_doctor_can_login_with_email(self, client, doctor_user):
        response = client.post(reverse("doctors:login"), {
            "identifier": doctor_user.profile.user.email,
            "password": PASSWORD,
        })
        assert response.status_code == 302
        assert response.url == reverse("doctors:dashboard")

    def test_patient_is_blocked_from_doctor_login(self, client, patient_user):
        response = client.post(reverse("doctors:login"), {
            "identifier": patient_user.profile.user.phone_number,
            "password": PASSWORD,
        })
        assert response.status_code == 200
        assert "_auth_user_id" not in client.session

    def test_wrong_password_fails(self, client, doctor_user):
        response = client.post(reverse("doctors:login"), {
            "identifier": doctor_user.profile.user.phone_number,
            "password": "wrong-one",
        })
        assert response.status_code == 200
        assert "_auth_user_id" not in client.session


@pytest.mark.django_db
class TestDoctorOTPLoginRequestView:
    def test_doctor_receives_otp_by_phone(self, client, doctor_user):
        response = client.post(reverse("doctors:otp_login"), {
            "identifier": doctor_user.profile.user.phone_number,
        })
        assert response.status_code == 302
        assert response.url == reverse("accounts:verify_otp")
        assert client.session["otp_purpose"] == "otp_login"
        assert client.session["otp_user_id"] == doctor_user.profile.user.id

    def test_doctor_receives_otp_by_email(self, client, doctor_user):
        response = client.post(reverse("doctors:otp_login"), {
            "identifier": doctor_user.profile.user.email,
        })
        assert response.status_code == 302
        assert response.url == reverse("accounts:verify_otp")
        assert client.session["otp_purpose"] == "otp_login"

    def test_unknown_identifier_shows_error(self, client):
        response = client.post(reverse("doctors:otp_login"), {"identifier": "09199999999"})
        assert response.status_code == 200
        assert "otp_user_id" not in client.session

    def test_patient_identifier_is_blocked(self, client, patient_user):
        response = client.post(reverse("doctors:otp_login"), {
            "identifier": patient_user.profile.user.phone_number,
        })
        assert response.status_code == 200
        assert "otp_user_id" not in client.session

    def test_full_flow_logs_doctor_in_and_redirects_to_dashboard(self, client, doctor_user):
        user = doctor_user.profile.user
        client.post(reverse("doctors:otp_login"), {"identifier": user.phone_number})

        otp = OTP.objects.get(user=user, purpose="otp_login", is_used=False)
        response = client.post(reverse("accounts:verify_otp"), {"code": otp.code})

        assert response.status_code == 302
        assert response.url == reverse("accounts:redirect_after_login")
        assert client.session["_auth_user_id"] == str(user.id)

        redirect_response = client.get(reverse("accounts:redirect_after_login"))
        assert redirect_response.status_code == 302
        assert redirect_response.url == reverse("doctors:dashboard")


@pytest.mark.django_db
class TestSearchDoctorsView:
    def test_lists_active_doctors(self, client, doctor_user):
        response = client.get(reverse("doctors:search"))
        assert response.status_code == 200
        assert doctor_user in response.context["doctors"]

    def test_inactive_doctor_excluded(self, client, doctor_user):
        doctor_user.is_active = False
        doctor_user.save()
        response = client.get(reverse("doctors:search"))
        assert doctor_user not in response.context["doctors"]

    def test_filter_by_name(self, client, doctor_user):
        response = client.get(reverse("doctors:search"), {"q": "تست"})
        assert doctor_user in response.context["doctors"]

        response = client.get(reverse("doctors:search"), {"q": "نام‌کاملا‌متفاوت"})
        assert doctor_user not in response.context["doctors"]

    def test_filter_by_specialty(self, client, doctor_user, specialty):
        response = client.get(reverse("doctors:search"), {"specialty": specialty.id})
        assert doctor_user in response.context["doctors"]


@pytest.mark.django_db
class TestDoctorDetailView:
    def test_returns_200_for_existing_doctor(self, client, doctor_user):
        response = client.get(reverse("doctors:detail", args=[doctor_user.pk]))
        assert response.status_code == 200
        assert response.context["doctor"] == doctor_user

    def test_returns_404_for_missing_doctor(self, client):
        response = client.get(reverse("doctors:detail", args=[999999]))
        assert response.status_code == 404

    def test_free_slot_appears_in_context(self, client, doctor_user, free_time_slot):
        response = client.get(reverse("doctors:detail", args=[doctor_user.pk]))
        all_slots = [s for slots in response.context["slots_by_date"].values() for s in slots]
        assert free_time_slot in all_slots


@pytest.mark.django_db
class TestDoctorOnlyAccess:


    def test_anonymous_user_redirected_to_login(self, client):
        response = client.get(reverse("doctors:dashboard"))
        assert response.status_code == 302
        assert reverse("accounts:login") in response.url

    def test_patient_cannot_access_dashboard(self, client, patient_user):
        client.force_login(patient_user.profile.user)
        response = client.get(reverse("doctors:dashboard"))
        assert response.status_code == 302
        assert response.url == reverse("accounts:login")

    def test_doctor_can_access_dashboard(self, client, doctor_user):
        client.force_login(doctor_user.profile.user)
        response = client.get(reverse("doctors:dashboard"))
        assert response.status_code == 200

    def test_patient_cannot_access_working_hours(self, client, patient_user):
        client.force_login(patient_user.profile.user)
        response = client.get(reverse("doctors:working_hours"))
        assert response.status_code == 302
        assert response.url == reverse("accounts:login")
