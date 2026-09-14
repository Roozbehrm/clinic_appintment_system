from django.db import models
from accounts.models import Profile


class Patient(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="patient")
    birth_date = models.DateField("تاریخ تولد", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "بیمار"
        verbose_name_plural = "بیماران"

    def __str__(self):
        return self.profile.full_name or self.profile.user.phone_number
