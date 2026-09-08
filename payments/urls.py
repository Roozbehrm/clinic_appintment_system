from django.urls import path
from payments.views import WalletDetailView , WalletDepositView


app_name = 'payments' 

urlpatterns = [
    path('wallet/',
        WalletDetailView.as_view(), 
        name = 'wallet_detail'),

    path(
        'wallet/deposit/',
        WalletDepositView.as_view(),
        name='wallet_deposit'
    ), 

    
]