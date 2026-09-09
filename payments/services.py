from payments.models import Transaction,Wallet
from django.core.exceptions import ValidationError
from django.db import transaction as db_transaction 

 #افزایش موجودی کیف پول 
def deposit(wallet,amount):

    with db_transaction.atomic():

        wallet = Wallet.objects.select_for_update().get(
             pk = wallet.pk
        )
             
        wallet.balance += amount
        wallet.save()

        Transaction.objects.create(
            wallet_id = wallet.id,
            appointment_id = None,
            amount = amount,
            type = 'deposit',
            status = 'success' ,
        )
    return wallet 


#  پرداخت هزینه نوبت 
def pay_for_appointment(wallet,price,appointment):

    with db_transaction.atomic():
    
        wallet = Wallet.objects.select_for_update().get(
                pk = wallet.pk
        )

        if wallet.balance < price :
            raise ValidationError('موجودی کیف پول کافی نیست.')
        
        wallet.balance -= price
        wallet.save()
        
        Transaction.objects.create(
                wallet_id = wallet.id,
                appointment_id = appointment.id,
                amount = price,
                type = 'payment',
                status = 'success' ,
            )

    return wallet 
 

# بازگشت وجه
def refund_appointment(wallet,price,appointment ):

    with db_transaction.atomic():
        wallet = Wallet.objects.select_for_update().get(
            pk = wallet.pk
        )
        
        wallet.balance += price
        wallet.save()

        Transaction.objects.create(
                        wallet_id = wallet.id,
                        appointment_id = appointment.id,
                        amount = price,
                        type = 'refund',
                        status = 'success' ,
                    )
    return wallet  

        