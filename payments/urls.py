from django.urls import path
from payments.views import WalletDetailView , WallletTopUpView


app_name = 'payments' 

urlpatterns = [
    path('wallet/',
        WalletDetailView.as_view(), 
        name = 'wallet_detail'), 

    path('wallet/top-up/',
        WallletTopUpView.as_view(),
        name = 'wallet_top_up'),
]