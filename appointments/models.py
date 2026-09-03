from django.db import models

# TASK T3.2 (Mahyar) 
class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'در انتظار پرداخت'),
        ('confirmed', 'تایید شده'),
        ('canceled', 'لغو شده'),
        ('completed', 'پایان یافته'),
    )

    # ارجاع به مدل بیمار (روزبه) 
    patient = models.ForeignKey('patients.Patient', on_delete=models.PROTECT, related_name='appointments',verbose_name='بیمار')
    # ارجاع به مدل زمان‌بندی (علی)
    time_slot = models.OneToOneField('doctors.TimeSlot', on_delete=models.PROTECT, related_name='appointment',verbose_name='بازه زمانی')

    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='هزینه ویزیت')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')

    class Meta:
        verbose_name = 'نوبت'
        verbose_name_plural = 'نوبت‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return f"نوبت {self.id} - بیمار: {self.patient_id} - وضعیت: {self.get_status_display()}"
    


# ============ توجه ============
# تا زمانی که روزبه و علی مرج نشده کد هاشون 
# makemigrations 
# رو نزنید چون جنگو دنبال مدل های اونا میگرده 
# # ============ توجه ============
