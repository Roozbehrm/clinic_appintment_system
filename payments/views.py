from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View

from .forms import DepositForm
from .services import deposit


class WalletDetailView(LoginRequiredMixin, View):
    login_url = "accounts:login"

    def get(self, request):
        wallet = request.user.profile.patient.wallet
        transactions = wallet.transactions.all()[:30]
        form = DepositForm()
        return render(request, "payments/wallet.html", {
            "wallet": wallet, "transactions": transactions, "form": form,
        })


class WalletDepositView(LoginRequiredMixin, View):
    login_url = "accounts:login"

    def post(self, request):
        wallet = request.user.profile.patient.wallet
        form = DepositForm(request.POST)
        if form.is_valid():
            # اینجا محل اتصال به درگاه واقعی پرداخت است (زرین‌پال و ...).
            # فعلاً به‌صورت شبیه‌سازی‌شده، مستقیم شارژ می‌شود.
            deposit(wallet, form.cleaned_data["amount"])
            messages.success(request, "کیف پول با موفقیت شارژ شد.")
        return redirect("payments:wallet_detail")
