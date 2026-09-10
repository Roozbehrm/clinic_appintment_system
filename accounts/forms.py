from django import forms 




class PhoneOnlyForm(forms.Form):

    phone_number = forms.CharField(
        max_length=11 , label = 'شماره موبایل'
        )

    def clean_phone_number(self):

        phone = self.cleaned_data.get('phone_number')

        if not phone.isdigit():
            raise forms.ValidationError ( 'شماره موبایل باید فقط شامل اعداد باشد.')

        if  len(phone) != 11:
            raise forms.ValidationError ( 'شماره موبایل باید ۱۱ رقم باشد.')


        if not phone.startswith('09'):
            raise forms.ValidationError ( 'شماره موبایل معتبر نیست.')

        return phone




