import pytest
from django.urls import reverse

from accounts.models import User


@pytest.fixture
def admin_client_logged_in(client, db):
    admin_user = User.objects.create_superuser(
        email="admin@example.com", password="AdminPass123!", phone_number="09120009999",
    )
    client.force_login(admin_user)
    return client


@pytest.mark.django_db
class TestDoctorAdminAddMessage:
 

    def _post_data(self, specialty, **overrides):
        data = {
            "phone_number": "09121110000",
            "email": "newdoc@example.com",
            "full_name": "پزشک تستی",
            "password": "",
            "mcc": "55555",
            "specialty": specialty.id,
            "bio": "",
            "consultation_fee": "200000",
            "is_active": "on",
        }
        data.update(overrides)
        return data

    def test_only_one_message_after_adding_doctor(self, admin_client_logged_in, specialty):
        response = admin_client_logged_in.post(
            reverse("admin:doctors_doctor_add"), self._post_data(specialty), follow=True,
        )
        page_messages = list(response.context["messages"])
        assert len(page_messages) == 1
        assert "پزشک تستی" in str(page_messages[0])

    def test_generated_password_is_shown_when_left_blank(self, admin_client_logged_in, specialty):
        response = admin_client_logged_in.post(
            reverse("admin:doctors_doctor_add"),
            self._post_data(specialty, phone_number="09121110001", email="newdoc2@example.com"),
            follow=True,
        )
        page_messages = list(response.context["messages"])
        assert len(page_messages) == 1
        assert "رمز عبور اولیه" in str(page_messages[0])

    def test_explicit_password_is_not_leaked_in_message(self, admin_client_logged_in, specialty):
        response = admin_client_logged_in.post(
            reverse("admin:doctors_doctor_add"),
            self._post_data(
                specialty, phone_number="09121110002", email="newdoc3@example.com",
                password="ChosenByStaff123",
            ),
            follow=True,
        )
        page_messages = list(response.context["messages"])
        assert len(page_messages) == 1
        assert "ChosenByStaff123" not in str(page_messages[0])