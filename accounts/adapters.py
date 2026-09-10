
import uuid
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from accounts.models import Profile
from patients.models import Patient
from payments.models import Wallet 
from doctors.models import Doctor  

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def populate_user(self,request,sociallogin,data):

        user = super().populate_user(
            request,
            sociallogin,
            data
        )

        if not user.phone_number:
            user.phone_number = (
                f'google_{uuid.uuid4().hex[:14]}'
            )

        user.is_verified = True

        return user


    def save_user(self, request,sociallogin,form=None):
        user = super().save_user(
            request,
            sociallogin,
            form
        )

        extra_data = sociallogin.account.extra_data
        full_name = extra_data.get('name', '')

        profile , created = Profile.objects.get_or_create(
        user_id=user,
        defaults={
            'full_name': full_name,
        }
        )

        is_patient = Patient.objects.filter(
            profile=profile
        ).exists()

        is_doctor = Doctor.objects.filter(
            profile_id=profile
        ).exists()

        if not is_patient and not is_doctor:

            patient = Patient.objects.create(
            profile_id=profile
        )

            Wallet.objects.get_or_create(
            patient_id=patient
        )

        return user
