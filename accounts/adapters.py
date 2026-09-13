from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):


    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        user.is_verified = True
        return user

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)

        from accounts.models import Profile
        from patients.models import Patient
        from payments.models import Wallet

        profile, _ = Profile.objects.get_or_create(user=user)
        full_name = sociallogin.account.extra_data.get("name", "")
        if full_name and not profile.full_name:
            profile.full_name = full_name
            profile.save()

        if not hasattr(profile, "patient") and not hasattr(profile, "doctor"):
            patient, _ = Patient.objects.get_or_create(profile=profile)
            Wallet.objects.get_or_create(patient=patient)

        return user
