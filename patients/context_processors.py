

def wallet_balance(request):

    if request.user.is_authenticated and request.user.is_patient: 

        wallet = request.user.profile.patient.wallet
        return {
            'wallet_balance' : wallet.balance
        }
    return {}