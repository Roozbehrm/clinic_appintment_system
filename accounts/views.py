from django.shortcuts import render,redirect
from django.views import View
from accounts.forms import PhoneOnlyForm
from accounts.models import OTP, User
import random
from django.conf import settings
from django.utils import timezone
from datetime import timedelta



class OTPLoginRequestView(View):

    def get(self,request):

        form = PhoneOnlyForm()

        return render(
            request,
            'accounts/otp_login.html',
            {'form':form}
        )

    def post(self,request):

        form = PhoneOnlyForm(request.POST)

        if form.is_valid():

            phone = form.cleaned_data.get('phone_number')
            try:
                user = User.objects.get(phone_number = phone)

            except User.DoesNotExist:

                form.add_error(
                    'phone_number', 'کاربری با این شماره موبایل وجود ندارد')

                return render(request,
                            'accounts/otp_login.html',
                          {'form':form})
                
            code = str(
                random.randint(100000,999999)
                )
                
            OTP.objects.create(
                user_id = user.id,
                code = code,
                purpose = 'otp_login',
                expires_at = timezone.now() + timedelta(
                    minutes= settings.OTP_EXPIRY_MINUTES 
                )
            )

            return redirect('accounts:verify_otp')
        
        return render(
            request,
            'accounts/otp_login.html',
            {'form': form}
        )



