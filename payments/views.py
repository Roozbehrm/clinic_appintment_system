from django.shortcuts import render
from django.views.generic import TemplateView , FormView
from payments.models import Transaction, Wallet
from payments.forms import WalletTopUpForm 
from django.urls import reverse_lazy 

class WalletDetailView(TemplateView):
    
    template_name = 'payments/templates/wallet_detail.html'
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        wallet = Wallet.objects.get(
            patient_id__profile_id__user=self.request.user
        )
        context['wallet'] = wallet

        context['transactions'] = Transaction.objects.filter(wallet_id=wallet.id).order_by('-created_at')

        return context 



class WallletTopUpView(FormView):
    template_name = 'payments/templates/top_up.html'
    form_class = WalletTopUpForm

    def form_valid(self,form):
        amount = form.cleaned_data['amount']
        wallet = Wallet.objects.get(
           patient_id__profile_id__user_id = self.request.user.id
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

        self.success_url = reverse_lazy(
            'payments:wallet_detail'
            
            )

        return super().form_valid(form)




