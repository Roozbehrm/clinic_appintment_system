from django.db import models
from accounts.models import Profile

class Patient(models.Model):

    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, verbose_name='پروفایل بیمار', related_name='patient_profile')
    birth_date = models.DateField(null=True, blank=True, verbose_name='تاریخ تولد')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ به‌روزرسانی')

    class Meta:
        verbose_name = 'بیمار'
        verbose_name_plural = 'بیماران'

    def __str__(self):
        return self.profile.full_name