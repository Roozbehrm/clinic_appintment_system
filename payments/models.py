from django.db import models

class Wallet(models.Model):
    patient_id = models.OneToOneField(to='patient' , related_name = 'wallet', on_delete=models.CASCADE, null =False)
    balance = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    def __repr__ (self):
        return f'Wallet balance for patient: {self.patient_id} is: {self.balance}'

class Transaction(models.Model):
    STATUS_CHOICES = [('success','success'), ('failed','failed'), ('pending','pending'),]
    TYPE_CHOICES = [('deposit','deposit'),('payment','payment'),('refund','refund'),]
    wallet_id = models.ForeignKey(to='Wallet', related_name='transaction', on_delete=models.CASCADE, null =False)
    appointment_id = models.ForeignKey(to='appointment', related_name='transactions', on_delete=models.CASCADE, null = True, blank = True)
    amount = models.DecimalField(max_digits=12, decimal_places=0)
    type = models.CharField(choices = TYPE_CHOICES,  max_length = 50)
    status = models.CharField(choices = STATUS_CHOICES, max_length=15)
    created_at = models.DateTimeField(auto_now_add = True)

    def __repr__(self):
        return f'appointment:{self.appointment_id} /n status:{self.status}'


