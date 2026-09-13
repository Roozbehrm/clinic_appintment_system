import pytest
from django.urls import reverse

from accounts.models import OTP, Profile, User
from accounts.services import issue_otp
from patients.models import Patient
from payments.models import Wallet

PASSWORD = "StrongPass123!"


def _set_session(client, **items):
    session = client.session
    for key, value in items.items():
        session[key] = value
    session.save()


@pytest.mark.django_db
class TestRegisterView:
    def test_get_renders_form(self, client):
        response = client.get(reverse("accounts:register"))
        assert response.status_code == 200

    def test_post_valid_data_creates_unverified_patient_and_sends_otp(self, client):
        response = client.post(reverse("accounts:register"), {
            "phone_number": "09131234567",
            "email": "newuser@example.com",
            "password": PASSWORD,
            "password_confirm": PASSWORD,
        })

        assert response.status_code == 302
        assert response.url == reverse("accounts:verify_otp")

        user = User.objects.get(phone_number="09131234567")
        assert user.is_verified is False
        assert user.email == "newuser@example.com"
        assert Patient.objects.filter(profile__user=user).exists()
        assert Wallet.objects.filter(patient__profile__user=user).exists()
        assert OTP.objects.filter(user=user, purpose="register").exists()

        assert client.session["otp_user_id"] == user.id
        assert client.session["otp_purpose"] == "register"

    def test_post_mismatched_passwords_fails(self, client):
        response = client.post(reverse("accounts:register"), {
            "phone_number": "09131234568",
            "email": "another@example.com",
            "password": PASSWORD,
            "password_confirm": "somethingElse123!",
        })
        assert response.status_code == 200  # 
        assert not User.objects.filter(phone_number="09131234568").exists()

    def test_post_duplicate_verified_phone_fails(self, client, patient_user):
        response = client.post(reverse("accounts:register"), {
            "phone_number": patient_user.profile.user.phone_number,
            "email": "brandnew@example.com",
            "password": PASSWORD,
            "password_confirm": PASSWORD,
        })
        assert response.status_code == 200
        form = response.context["form"]
        assert "phone_number" in form.errors


@pytest.mark.django_db
class TestVerifyOTPView:
    def test_correct_code_logs_user_in_and_verifies(self, client):
        user = User.objects.create(phone_number="09132222222", email="v1@example.com")
        user.set_password(PASSWORD)
        user.save()
        Profile.objects.create(user=user)
        otp = issue_otp(user, "register")

        _set_session(client, otp_user_id=user.id, otp_purpose="register")

        response = client.post(reverse("accounts:verify_otp"), {"code": otp.code})

        assert response.status_code == 302
        assert response.url == reverse("accounts:redirect_after_login")

        user.refresh_from_db()
        assert user.is_verified is True
        assert "otp_user_id" not in client.session

    def test_wrong_code_does_not_verify_or_login(self, client):
        user = User.objects.create(phone_number="09132222223", email="v2@example.com")
        Profile.objects.create(user=user)
        issue_otp(user, "register")

        _set_session(client, otp_user_id=user.id, otp_purpose="register")

        response = client.post(reverse("accounts:verify_otp"), {"code": "000000"})

        assert response.status_code == 200
        user.refresh_from_db()
        assert user.is_verified is False

    def test_reset_password_purpose_redirects_to_set_new_password(self, client):
        user = User.objects.create(phone_number="09132222224", email="v3@example.com")
        Profile.objects.create(user=user)
        otp = issue_otp(user, "reset_password")

        _set_session(client, otp_user_id=user.id, otp_purpose="reset_password")

        response = client.post(reverse("accounts:verify_otp"), {"code": otp.code})

        assert response.status_code == 302
        assert response.url == reverse("accounts:set_new_password")
        assert client.session["reset_user_id"] == user.id


@pytest.mark.django_db
class TestLoginView:
    def test_login_with_phone_number(self, client, patient_user):
        response = client.post(reverse("accounts:login"), {
            "identifier": patient_user.profile.user.phone_number,
            "password": PASSWORD,
        })
        assert response.status_code == 302
        assert response.url == reverse("accounts:redirect_after_login")

    def test_login_with_email(self, client, patient_user):
        response = client.post(reverse("accounts:login"), {
            "identifier": patient_user.profile.user.email,
            "password": PASSWORD,
        })
        assert response.status_code == 302
        assert response.url == reverse("accounts:redirect_after_login")

    def test_wrong_password_fails(self, client, patient_user):
        response = client.post(reverse("accounts:login"), {
            "identifier": patient_user.profile.user.phone_number,
            "password": "wrong-password",
        })
        assert response.status_code == 200
        assert "_auth_user_id" not in client.session

    def test_doctor_account_is_blocked_from_patient_login(self, client, doctor_user):
        response = client.post(reverse("accounts:login"), {
            "identifier": doctor_user.profile.user.phone_number,
            "password": PASSWORD,
        })
        assert response.status_code == 200
        assert "_auth_user_id" not in client.session

    def test_unverified_user_gets_redirected_to_otp(self, client):
        user = User.objects.create(phone_number="09133333333", email="unv@example.com")
        user.set_password(PASSWORD)
        user.is_verified = False
        user.save()
        Profile.objects.create(user=user)

        response = client.post(reverse("accounts:login"), {
            "identifier": "09133333333",
            "password": PASSWORD,
        })
        assert response.status_code == 302
        assert response.url == reverse("accounts:verify_otp")
        assert OTP.objects.filter(user=user, purpose="login").exists()


@pytest.mark.django_db
class TestOTPLoginRequestView:
    def test_existing_patient_receives_otp_by_phone(self, client, patient_user):
        response = client.post(reverse("accounts:otp_login"), {
            "identifier": patient_user.profile.user.phone_number,
        })
        assert response.status_code == 302
        assert response.url == reverse("accounts:verify_otp")
        assert client.session["otp_purpose"] == "otp_login"

    def test_existing_patient_receives_otp_by_email(self, client, patient_user):
        response = client.post(reverse("accounts:otp_login"), {
            "identifier": patient_user.profile.user.email,
        })
        assert response.status_code == 302
        assert response.url == reverse("accounts:verify_otp")
        assert client.session["otp_purpose"] == "otp_login"

    def test_unknown_identifier_shows_error(self, client):
        response = client.post(reverse("accounts:otp_login"), {"identifier": "09199999999"})
        assert response.status_code == 200
        assert "otp_user_id" not in client.session

    def test_doctor_identifier_is_blocked(self, client, doctor_user):
        response = client.post(reverse("accounts:otp_login"), {
            "identifier": doctor_user.profile.user.phone_number,
        })
        assert response.status_code == 200
        assert "otp_user_id" not in client.session


@pytest.mark.django_db
class TestRedirectAfterLoginView:
    def test_doctor_goes_to_dashboard(self, client, doctor_user):
        client.force_login(doctor_user.profile.user)
        response = client.get(reverse("accounts:redirect_after_login"))
        assert response.status_code == 302
        assert response.url == reverse("doctors:dashboard")

    def test_patient_goes_to_doctor_search(self, client, patient_user):
        client.force_login(patient_user.profile.user)
        response = client.get(reverse("accounts:redirect_after_login"))
        assert response.status_code == 302
        assert response.url == reverse("doctors:search")

    def test_user_without_role_goes_to_complete_profile(self, client):
        user = User.objects.create(phone_number="09134444444", email="norole@example.com", is_verified=True)
        Profile.objects.create(user=user)
        client.force_login(user)
        response = client.get(reverse("accounts:redirect_after_login"))
        assert response.status_code == 302
        assert response.url == reverse("accounts:complete_profile")
