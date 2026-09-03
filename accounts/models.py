from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
  
    phone_number = models.CharField(max_length=15, unique=True, null=False,verbose_name='شماره تلفن')
    email = models.EmailField(unique=True, null=False, verbose_name='ایمیل')
    is_verified = models.BooleanField(default=False, verbose_name='تایید شده')
    created_at = models.DateTimeField(auto_now_add=True , verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ به‌روزرسانی')

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

    def __str__(self):
        return self.username



class Profile(models.Model):
 
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='کاربر', related_name='profile')
    full_name = models.CharField(max_length=100, verbose_name='نام کامل')
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.jpg', null=True, blank=True, verbose_name='آواتار')
    national_code = models.CharField(max_length=10, null=True, blank=True, verbose_name='کد ملی')
    gender = models.CharField(max_length=10, choices=[('male', 'مرد'), ('female', 'زن')], null=True, blank=True, verbose_name='جنسیت')
    address = models.TextField(null=True, blank=True, verbose_name='آدرس')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ به‌روزرسانی')

    class Meta:
        verbose_name = 'پروفایل'
        verbose_name_plural = 'پروفایل‌ها'

    def __str__(self):
        return self.full_name



