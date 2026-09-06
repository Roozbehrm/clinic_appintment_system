from django.db import models
from accounts.models import Profile


class Specialty(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Doctor(models.Model):
    profile = models.OneToOneField(
        Profile, on_delete=models.CASCADE, related_name="doctor"
    )
    specialty = models.ForeignKey(
        Specialty, on_delete=models.PROTECT, related_name="doctors"
    )
    bio = models.TextField(blank=True, null=True)
    consulation_fee = models.DecimalField(max_length=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    office_address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.profile.full_name


class WorkingHour(models.Model):
    class DayOfWeek(models.IntegerChoices):
        SATURDAY = 0, "Saturday"
        SUNDAY = 1, "Sunday"
        MONDAY = 2, "Monday"
        TUESDAY = 3, "Tuesday"
        WEDNESDAY = 4, "Wednesday"
        THURSDAY = 5, "Thursday"
        FRIDAY = 6, "Friday"

    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name="working_hours"
    )
    day_of_week = models.IntegerField(choices=DayOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_duration_minutes = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "day_of_week", "start_time"],
                name="unique_doctor_day_start_time",
            )
        ]

    def __str__(self):
        return (
            f"{self.doctor} - "
            f"{self.get_day_of_week_display()} - "
            f"{self.start_time} to {self.end_time}"
        )


class TimeSlot(models.model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        BOOKED = "booked", "Booked"
        CANCELLED = "cancelled", "Cancelled"

    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name="time_slots"
    )
    working_hour = models.ForeignKey(
        WorkingHour,
        on_delete=models.CASCADE,
        related_name="time_slots",
        blank=True,
        null=True,
    )

    visit_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.AVAILABLE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "visit_date", "start_time"],
                name="unique_doctor_visit_date_start_time",
            )
        ]

    def __str__(self):
        return (
            f"{self.doctor} - "
            f"{self.visit_date} - "
            f"{self.start_time} to {self.end_time}"
        )
