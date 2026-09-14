
def wallet_balance(request):
    if request.user.is_authenticated and request.user.is_patient:
        wallet = getattr(request.user.profile.patient, "wallet", None)
        if wallet is not None:
            return {
                "wallet_balance": wallet.balance,
                "wallet_balance_display": f"{wallet.balance:,.0f}",
            }
    return {}