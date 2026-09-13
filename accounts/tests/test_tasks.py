import pytest

from accounts.tasks import send_email_task, send_sms_task


@pytest.mark.django_db
class TestSendSmsTask:
    def test_delivers_to_locmem_outbox(self):
        from sms.backends import locmem

        send_sms_task("09121234567", "متن تست")

        assert len(locmem.outbox) == 1
        assert locmem.outbox[0].phone_number == "09121234567"
        assert "متن تست" in locmem.outbox[0].message

    def test_exception_in_backend_is_swallowed(self, monkeypatch):

        def boom(*args, **kwargs):
            raise RuntimeError("SMS gateway down")

        monkeypatch.setattr("accounts.tasks.send_sms", boom)

        send_sms_task("09121234567", "متن تست")


@pytest.mark.django_db
class TestSendEmailTask:
    def test_delivers_to_mail_outbox(self, mailoutbox):
        send_email_task("موضوع تست", "متن تست", ["a@example.com"])

        assert len(mailoutbox) == 1
        assert mailoutbox[0].subject == "موضوع تست"
        assert mailoutbox[0].to == ["a@example.com"]

    def test_exception_is_swallowed(self, monkeypatch):
        def boom(*args, **kwargs):
            raise RuntimeError("SMTP down")

        monkeypatch.setattr("accounts.tasks.send_mail", boom)

        send_email_task("موضوع", "متن", ["a@example.com"])
