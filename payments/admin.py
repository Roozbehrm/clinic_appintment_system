from django.contrib import admin
from payments import models

@admin.register(models.Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient_id', 'balance', 'created_at', 'updated_at')
    

@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'wallet_id', 'appointment_id', 'amount', 'type', 'status', 'created_at')


