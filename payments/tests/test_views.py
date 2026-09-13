from decimal import Decimal

import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestWalletDetailView:
    def test_requires_login(self, client):
        response = client.get(reverse("payments:wallet_detail"))
        assert response.status_code == 302

    def test_shows_own_wallet(self, client, patient_user):
        client.force_login(patient_user.profile.user)
        response = client.get(reverse("payments:wallet_detail"))
        assert response.status_code == 200
        assert response.context["wallet"] == patient_user.wallet


@pytest.mark.django_db
class TestWalletDepositView:
    def test_deposit_increases_balance(self, client, patient_user):
        client.force_login(patient_user.profile.user)
        starting_balance = patient_user.wallet.balance

        response = client.post(reverse("payments:wallet_deposit"), {"amount": "50000"})

        assert response.status_code == 302
        assert response.url == reverse("payments:wallet_detail")
        patient_user.wallet.refresh_from_db()
        assert patient_user.wallet.balance == starting_balance + Decimal("50000")

    def test_amount_below_minimum_is_rejected(self, client, patient_user):
        client.force_login(patient_user.profile.user)
        starting_balance = patient_user.wallet.balance

        client.post(reverse("payments:wallet_deposit"), {"amount": "500"})  # کمتر از حداقل ۱۰۰۰

        patient_user.wallet.refresh_from_db()
        assert patient_user.wallet.balance == starting_balance
