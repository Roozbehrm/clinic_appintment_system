from django.db import models
from accounts.models import Profile

WEEKDAYS = [
    (0, "شنبه"), (1, "یکشنبه"), (2, "دوشنبه"), (3, "سه‌شنبه"),
    (4, "چهارشنبه"), (5, "پنجشنبه"), (6, "جمعه"),
]
# پایتون weekday(): Monday=0 ... Sunday=6  -> نگاشت به شنبه=0
PY_WEEKDAY_TO_OUR = {5: 0, 6: 1, 0: 2, 1: 3, 2: 4, 3: 5, 4: 6}


class Specialty(models.Model):
    name = models.CharField("نام تخصص", max_length=100, unique=True)
    description = models.TextField("توضیحات", blank=True)

    class Meta:
        verbose_name = "تخصص"
        verbose_name_plural = "تخصص‌ها"

    def __str__(self):
        return self.name


class Doctor(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="doctor")
    specialty = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True,
                                   related_name="doctors")
    mcc = models.CharField("شماره نظام پزشکی", max_length=20, unique=True)
    bio = models.TextField("بیوگرافی", blank=True)
    consultation_fee = models.DecimalField("هزینه ویزیت", max_digits=12, decimal_places=0, default=0)
    is_active = models.BooleanField("فعال", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "پزشک"
        verbose_name_plural = "پزشکان"

    def __str__(self):
        return self.profile.full_name or self.profile.user.phone_number

    @property
    def average_rating(self):
        from reviews.models import Review
        agg = Review.objects.filter(appointment__time_slot__doctor=self).aggregate(
            models.Avg("rating"))
        return round(agg["rating__avg"] or 0, 1)

    @property
    def review_count(self):
        from reviews.models import Review
        return Review.objects.filter(appointment__time_slot__doctor=self).count()


class WorkingHour(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="working_hours")
    day_of_week = models.IntegerField("روز هفته", choices=WEEKDAYS)
    start_time = models.TimeField("ساعت شروع")
    end_time = models.TimeField("ساعت پایان")
    slot_duration_minutes = models.PositiveIntegerField("مدت هر نوبت (دقیقه)", default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "ساعت کاری"
        verbose_name_plural = "ساعات کاری"
        ordering = ["day_of_week", "start_time"]
        unique_together = ["doctor", "day_of_week", "start_time", "end_time"]

    def __str__(self):
        return f"{self.doctor} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class TimeSlot(models.Model):
    STATUS_CHOICES = [("free", "خالی"), ("booked", "رزرو شده"), ("cancelled", "لغو شده")]

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="time_slots")
    working_hours = models.ForeignKey(WorkingHour, on_delete=models.SET_NULL, null=True, related_name="time_slots")
    visit_date = models.DateField(verbose_name="تاریخ ویزیت")
    start_time = models.TimeField(verbose_name="ساعت شروع")
    end_time = models.TimeField(verbose_name="ساعت پایان")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="free", verbose_name="وضعبت")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "نوبت خالی"
        verbose_name_plural = "نوبت‌های خالی"
        ordering = ["visit_date", "start_time"]
        unique_together = ["doctor", "visit_date", "start_time"]

    def __str__(self):
        return f"{self.doctor} - {self.visit_date} {self.start_time}"

    @property
    def is_free(self):
        return self.status == "free"
