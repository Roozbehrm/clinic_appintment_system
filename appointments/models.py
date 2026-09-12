from django.db import models
from patients.models import Patient
from doctors.models import TimeSlot


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("pending", "در انتظار پرداخت"),
        ("confirmed", "تایید شده"),
        ("cancelled", "لغو شده"),
        ("completed", "انجام شده"),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")
    time_slot = models.OneToOneField(TimeSlot, on_delete=models.CASCADE, related_name="appointment")
    price = models.DecimalField("مبلغ", max_digits=12, decimal_places=0)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "نوبت"
        verbose_name_plural = "نوبت‌ها"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.patient} - {self.time_slot}"

    @property
    def is_reviewable(self):
        return self.status == "completed" and not hasattr(self, "review")