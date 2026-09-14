import pytest 
from django.core.exceptions import ValidationError
from decimal import Decimal

from payments.services import (
    deposit,
    pay_for_appointment,
    refund_appointment,
)
from payments.models import Transaction 
from appointments.models import Appointment



@pytest.mark.django_db
class TestDeposit:
    def test_increases_balance_and_logs_transaction(self, patient_user):
        wallet = patient_user.wallet
        starting_balance = wallet.balance

        deposit(wallet, Decimal("50000"))

        wallet.refresh_from_db()
        assert wallet.balance == starting_balance + Decimal("50000")
        assert Transaction.objects.filter(wallet=wallet, type="deposit", amount=Decimal("50000")).exists()


@pytest.mark.django_db
class Test_pay_for_appointment:

    def test_pay_for_appointment_decrease_wallet_balance(self,patient_user,free_time_slot):

        wallet = patient_user.wallet 
        old_balance = wallet.balance

        price = Decimal("50000")

        appointment= Appointment.objects.create(
            patient = patient_user ,
            time_slot =  free_time_slot,
            price= price,
            status = 'pending',
        )

        pay_for_appointment(wallet, appointment, price)
        
        wallet.refresh_from_db()

        assert wallet.balance == old_balance - price
        assert Transaction.objects.filter(
                    wallet = wallet.id,
                    appointment = appointment.id,
                    type="payment",
                ).exists()

    def test_pay_for_appointment_insufficient_balance(self,patient_user,free_time_slot):

        wallet = patient_user.wallet

        price = Decimal("2000000")

        appointment= Appointment.objects.create(
                    patient = patient_user ,
                    time_slot =  free_time_slot,
                    price= price,
                    status = 'pending',
                )

        with pytest.raises(ValidationError):
           
           pay_for_appointment(wallet, appointment, price)

        wallet.refresh_from_db()

        assert wallet.balance == Decimal("1000000")

        assert not Transaction.objects.filter(
            wallet=wallet.id,
            appointment=appointment.id,
            type="payment",
        ).exists()



@pytest.mark.django_db
class Test_refund_appointment:

    def test_increase_wallet_balance(self,patient_user,free_time_slot):

        wallet = patient_user.wallet
        old_balance = wallet.balance

        price = Decimal("50000")

        appointment= Appointment.objects.create(
                            patient = patient_user ,
                            time_slot =  free_time_slot,
                            price= price,
                            status = 'cancelled',
                        )

        refund_appointment(wallet, appointment, price)

        wallet.refresh_from_db()

        assert wallet.balance ==  old_balance +  price
        assert Transaction.objects.filter(
                    wallet=wallet.id,
                    appointment=appointment.id,
                    type="refund",
                    amount=Decimal("50000")
                ).exists()


    
