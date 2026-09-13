import pytest

from accounts.models import OTP, User
from accounts.services import (
    find_user_by_identifier,
    issue_otp,
    send_appointment_confirmation_email,
)
from sms.backends import locmem


@pytest.mark.django_db
class TestFindUserByIdentifier:
    def test_finds_by_phone_number(self):
        user = User.objects.create(phone_number="09121112222", email="x@example.com")
        found = find_user_by_identifier("09121112222")
        assert found == user

    def test_finds_by_email_case_insensitive(self):
        user = User.objects.create(phone_number="09121112223", email="Person@Example.com")
        found = find_user_by_identifier("person@example.com")
        assert found == user

    def test_returns_none_for_unknown_identifier(self):
        assert find_user_by_identifier("09190000000") is None
        assert find_user_by_identifier("nobody@example.com") is None

    def test_returns_none_for_empty_input(self):
        assert find_user_by_identifier("") is None
        assert find_user_by_identifier(None) is None


@pytest.mark.django_db
class TestIssueOTP:
    def test_creates_otp_and_delivers_via_sms_and_email(self):
        user = User.objects.create(phone_number="09121113333", email="y@example.com")

        otp = issue_otp(user, "register")

        assert OTP.objects.filter(user=user, purpose="register").count() == 1
        assert otp.code in locmem.outbox[0].message
        assert locmem.outbox[0].phone_number == user.phone_number

    def test_delivers_via_email_when_user_has_email(self, mailoutbox):
        user = User.objects.create(phone_number="09121114444", email="z@example.com")
        otp = issue_otp(user, "login")

        assert len(mailoutbox) == 1
        assert otp.code in mailoutbox[0].body
        assert mailoutbox[0].to == ["z@example.com"]

    def test_previous_unused_otp_of_same_purpose_is_invalidated(self):
        user = User.objects.create(phone_number="09121115555", email="w@example.com")
        first_otp = issue_otp(user, "login")
        first_otp_id = first_otp.id
        second_otp = issue_otp(user, "login")

        assert not OTP.objects.filter(id=first_otp_id).exists()
        assert second_otp.is_used is False

    def test_otp_of_different_purpose_is_not_invalidated(self):
        user = User.objects.create(phone_number="09121116666", email="v@example.com")
        register_otp = issue_otp(user, "register")
        issue_otp(user, "login")

        register_otp.refresh_from_db()
        assert register_otp.is_used is False


@pytest.mark.django_db
class TestSendAppointmentConfirmationEmail:
    def test_sends_email_with_appointment_details(
        self, mailoutbox, doctor_user, patient_user, free_time_slot
    ):
        from appointments.models import Appointment

        appointment = Appointment.objects.create(
            patient=patient_user, time_slot=free_time_slot,
            price=200000, status="confirmed",
        )

        send_appointment_confirmation_email(appointment)

        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == ["patient@example.com"]
        assert "تاییدیه" in mailoutbox[0].subject

    def test_does_nothing_when_patient_has_no_email(
        self, mailoutbox, doctor_user, patient_user, free_time_slot
    ):
        from appointments.models import Appointment

        patient_user.profile.user.email = ""

        User.objects.filter(pk=patient_user.profile.user.pk).update(email="")

        appointment = Appointment.objects.create(
            patient=patient_user, time_slot=free_time_slot,
            price=200000, status="confirmed",
        )

        send_appointment_confirmation_email(appointment)

        assert len(mailoutbox) == 0
