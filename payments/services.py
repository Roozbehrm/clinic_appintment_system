from django.db import transaction as db_transaction
from django.core.exceptions import ValidationError

from .models import Wallet, Transaction


def deposit(wallet, amount):
    with db_transaction.atomic():
        wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)
        wallet.balance += amount
        wallet.save()
        Transaction.objects.create(wallet=wallet, amount=amount, type="deposit", status="success")
    return wallet


def pay_for_appointment(wallet, appointment, amount):
    with db_transaction.atomic():
        wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)
        if wallet.balance < amount:
            raise ValidationError("موجودی کیف پول کافی نیست.")
        wallet.balance -= amount
        wallet.save()
        Transaction.objects.create(
            wallet=wallet, appointment=appointment, amount=amount,
            type="payment", status="success",
        )
    return wallet


def refund_appointment(wallet, appointment, amount):
    with db_transaction.atomic():
        wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)
        wallet.balance += amount
        wallet.save()
        Transaction.objects.create(
            wallet=wallet, appointment=appointment, amount=amount,
            type="refund", status="success",
        )
    return wallet