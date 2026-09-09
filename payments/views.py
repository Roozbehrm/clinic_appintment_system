from django.shortcuts import render
from django.views.generic import TemplateView , FormView
from payments.models import Transaction, Wallet
from payments.forms import WalletTopUpForm 
from django.urls import reverse_lazy 
from payments.services import deposit

class WalletDetailView(TemplateView):
    
    template_name = 'payments/templates/wallet_detail.html'
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # فرم افزایش موجودی
        context['form'] = WalletTopUpForm()

        # پیدا کردن کیف پول فرد لاگین شده
        wallet = Wallet.objects.get(
            patient_id__profile_id__user=self.request.user
        )
        context['wallet'] = wallet

        # تاریخچه ی تراکنش: 
        context['transactions'] = Transaction.objects.filter(wallet_id=wallet.id).order_by('-created_at')

        return context 



class WalletDepositView(FormView):
    
    form_class = WalletTopUpForm

    def form_valid(self,form):
        
        amount = form.cleaned_data['amount']
        wallet = Wallet.objects.get(
           patient_id__profile_id__user_id = self.request.user.id
            )
        
        deposit (wallet,amount)

        self.success_url = reverse_lazy(
            'payments:wallet_detail'
            
            )

        return super().form_valid(form)




