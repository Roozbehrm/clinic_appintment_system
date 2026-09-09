from django.db import models
from accounts.models import Profile

WEEKDAYS = [
    (0, "شنبه"),
    (1, "یکشنبه"),
    (2, "دوشنبه"),
    (3, "سه شنبه"),
    (4, "چهارشنبه"),
    (5, "پنج شنبه"),
    (6, "جمعه"),
]

PY_WEEKDAY_TO_OUR = {
    5: 0,
    6: 1,
    0: 2,
    1: 3,
    2: 4,
    3: 5,
    4: 6,
}


class Specialty(models.Model):

    name = models.CharField(
        max_length=255,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    def __str__(self):
        return self.name


class Doctor(models.Model):

    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name="doctor",
    )

    specialty = models.ForeignKey(
        Specialty,
        on_delete=models.PROTECT,
        related_name="doctors",
    )

    bio = models.TextField(
        blank=True,
    )

    consultation_fee = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    @property
    def average_rating(self):
        from reviews.models import Review

        result = Review.objects.filter(appointment__time_slot__doctor=self).aggregate(
            average=models.Avg("rating")
        )

        return result["average"] or 0

    @property
    def review_count(self):
        from reviews.models import Review

        return Review.objects.filter(appointment__time_slot__doctor=self).count()

    def __str__(self):
        return self.profile.full_name


class WorkingHour(models.Model):

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="working_hours",
    )

    day_of_week = models.IntegerField(
        choices=WEEKDAYS,
    )

    start_time = models.TimeField()

    end_time = models.TimeField()

    slot_duration_minutes = models.PositiveIntegerField(
        default=30,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return (
            f"{self.doctor} - "
            f"{self.get_day_of_week_display()} "
            f"{self.start_time} تا {self.end_time}"
        )


class TimeSlot(models.Model):
    STATUS_FREE = "free"
    STATUS_BOOKED = "booked"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_FREE, "آزاد"),
        (STATUS_BOOKED, "رزرو شده"),
        (STATUS_CANCELLED, "لغو شده"),
    ]

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="time_slot",
    )

    working_hours = models.ForeignKey(
        WorkingHour,
        on_delete=models.SET_NULL,
        related_name="time_slots",
    )

    visit_date = models.DateField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_FREE,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "visit_date", "start_time"],
                name="unique_doctor_visit_date_start_time",
            )
        ]

    @property
    def is_free(self):
        return self.status == self.STATUS_FREE

    def __str__(self):
        return (
            f"{self.doctor} - "
            f"{self.visit_date} "
            f"{self.start_time}-{self.end_time}"
        )
